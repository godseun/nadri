import re
import json
import asyncio
from typing import AsyncGenerator, List

from requests.exceptions import RequestException
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import ScoredPoint
from qdrant_client.models import Record
from sentence_transformers import SentenceTransformer

from src.services.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableGenerator

from src.config import settings

def clean_chunk(chunk: str) -> str:
    # <think> 태그 및 내용 제거
    cleaned_chunk = re.sub(r'<think>.*?</think>', '', chunk, flags=re.DOTALL)
    return cleaned_chunk

class ChatService:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embedding_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.llm = get_llm()
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 서울에 대한 정보를 잘 알고 있는 여행/행사 가이드입니다."),
            ("system", "응답은 [{question_with_context}] 내용을 참고하여 한국어로 된 Markdown 형식으로 작성해주세요."),
            ("system", "응답은 Markdown 형식으로 작성해주세요. 다음 지침을 따르세요:"),
            ("system", "1. 제목은 `#` (대제목) 또는 `##` (중제목)을 사용하세요."),
            ("system", "2. 어울리는 이모지를 제목 앞에 추가하세요."),
            ("system", "3. 목록은 `-` 또는 `*`를 사용하고, 필요하면 중첩 목록을 만드세요."),
            ("system", "4. 중요한 내용은 `**굵게**` 표시하고, 강조할 내용은 `*기울임*`으로 표시하세요."),
            ("system", "5. 코드나 기술적인 내용은 백틱 3개(```)로 감싸서 코드 블록을 사용하세요."),
            # ("system", "6. 불필요한 서론이나 결론 없이 질문에 대한 핵심 답변부터 시작해주세요."),
            ("system", """예시: `\n# 서울의 명소 \n- **남산타워**: 서울의 상징. \n- **경복궁**: 조선 시대 궁궐.`"""),
            ("system", "모르면 모른다고 답해주세요."),
            ("ai", "나는 심심해서 여행이나 축제에 가고싶어한다."),
            ("human", "{human_question}")
        ])
        self.chain: RunnableGenerator[str, str] = self.prompt_template | self.llm | StrOutputParser()

    async def q(self, query: str) -> AsyncGenerator[str, None]:
        # 벡터 검색
        query_vector = self.embedding_model.encode(query).tolist()
        vector_search_result: List[ScoredPoint] = self.qdrant_client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=5,
            score_threshold=0.5,  # 점수 임계값 설정
        )

        # 키워드 검색 (scroll 사용)
        keyword_search_result: List[Record] = self.qdrant_client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="text",
                        match=models.MatchText(text=query)
                    )
                ]
            ),
            limit=5,
            with_payload=True
        )

        keyword_search_result = keyword_search_result[0]

        # 결과 통합 및 중복 제거
        combined_results = {}
        for r in vector_search_result:
            combined_results[r.id] = r
        for r in keyword_search_result:
            combined_results[r.id] = r

        if not combined_results:
            yield "data: 검색 결과가 없습니다.\n\n"
            yield "data: [DONE]\n\n"
            return

        # 통합된 결과를 리스트로 변환
        search_result = list(combined_results.values())

        # context 자르기
        tokenizer = self.embedding_model._first_module().tokenizer
        context: str = "\n".join([r.payload["text"] for r in search_result])

        def truncate_context(context_text: str, max_length: int = settings.MAX_CONTEXT_LENGTH, reserved: int = settings.RESERVED_TOKENS) -> str:
            max_context_tokens = max_length - reserved
            sentences = context_text.split("\n")
            total_tokens = 0
            result = []
            for sentence in sentences:
                tokens = tokenizer.encode(sentence, add_special_tokens=False)
                if total_tokens + len(tokens) > max_context_tokens:
                    break
                result.append(sentence)
                total_tokens += len(tokens)
            return "\n".join(result)

        final_context = truncate_context(context)
        prompt = f"다음 정보를 참고하여 질문에 답해주세요:\n\n{final_context}"

        try:
            response_iter = self.chain.stream({"question_with_context": prompt, "human_question": query})
            buffer = ""
            for chunk in response_iter:
                processed_chunk = clean_chunk(chunk)
                buffer += processed_chunk

                # Process buffer line by line
                while "\n" in buffer:
                    newline_index = buffer.find("\n")
                    line = buffer[:newline_index]
                    yield f"data: {line}\n\n"
                    buffer = buffer[newline_index + 1:]

                await asyncio.sleep(settings.STREAM_DELAY)

            if buffer:
                yield f"data: {buffer}\n\n"
        except RequestException as e:
            print(f"Connection error during LLM stream: {e}")
            error_message = json.dumps({"type": "error", "message": "AI 모델 연결에 실패했습니다. 서버 상태를 확인해주세요."})
            yield f"data: {error_message}\n\n"
        except Exception as e:
            print(f"Error during LLM stream: {e}")
            error_message = json.dumps({"type": "error", "message": "현재 AI 모델 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."})
            yield f"data: {error_message}\n\n"
        finally:
            yield "data: [DONE]\n\n"

chat_service = ChatService()

