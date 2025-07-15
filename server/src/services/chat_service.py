import re
import json
import asyncio
import yaml
from typing import AsyncGenerator, List

from requests.exceptions import RequestException
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_huggingface import HuggingFaceEmbeddings


from src.services.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableGenerator
from langchain_core.documents import Document

from src.config import settings

def clean_chunk(chunk: str) -> str:
    # <think> 태그 및 내용 제거
    cleaned_chunk = re.sub(r'<think>.*?</think>', '', chunk, flags=re.DOTALL)
    return cleaned_chunk

class ChatService:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embedding_model = HuggingFaceEmbeddings(model_name=settings.SENTENCE_TRANSFORMER_MODEL)
        self.llm = get_llm()

        # MultiQueryRetriever 설정
        with open("src/prompts/multi_query_prompt.yaml", 'r', encoding='utf-8') as f:
            multi_query_prompt_data = yaml.safe_load(f)
        
        multi_query_prompt = PromptTemplate(
            input_variables=["question"],
            template=multi_query_prompt_data["template"]
        )

        vectorstore = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embedding=self.embedding_model
        )
        
        self.retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(),
            llm=self.llm,
            prompt=multi_query_prompt
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 서울에 대한 정보를 잘 알고 있는 여행/행사 가이드입니다."),
            ("system", "응답은 [{question_with_context}] 내용을 참고하여 한국어로 된 Markdown 형식으로 작성해주세요."),
            ("system", "응답은 Markdown 형식으로 작성해주세요. 다음 지침을 따르세요:"),
            ("system", "1. 제목은 `#` (대제목) 또는 `##` (중제목)을 사용하세요."),
            ("system", "2. 어울리는 이모지를 제목 앞에 추가하세요."),
            ("system", "3. 목록은 `-` 또는 `*`를 사용하고, 필요하면 중첩 목록을 만드세요."),
            ("system", "4. 중요한 내용은 `**굵게**` 표시하고, 강조할 내용은 `*기울임*`으로 표시하세요."),
            ("system", "5. 코드나 기술적인 내용은 백틱 3개(```)로 감싸서 코드 블록을 사용하세요."),
            ("system", """예시: `\n# 서울의 명소 \n- **남산타워**: 서울의 상징. \n- **경복궁**: 조선 시대 궁궐.`"""),
            ("system", "모르면 모른다고 답해주세요."),
            ("ai", "나는 심심해서 여행이나 축제에 가고싶어한다."),
            ("human", "{human_question}")
        ])
        self.chain: RunnableGenerator[str, str] = self.prompt_template | self.llm | StrOutputParser()

    async def _handle_error(self, e: Exception, message: str) -> List[str]:
        print(f"Error: {e}")
        error_message = json.dumps({"type": "error", "message": message})
        return [f"data: {error_message}\n\n"]

    async def q(self, query: str) -> AsyncGenerator[str, None]:
        try:
            # MultiQueryRetriever를 사용하여 관련 문서 검색
            try:
                retrieved_docs: List[Document] = await asyncio.to_thread(self.retriever.invoke, query)
            except Exception as e:
                for chunk in await self._handle_error(e, "문서 검색 중 오류가 발생했습니다."):
                    yield chunk
                return

            if not retrieved_docs:
                yield "data: 검색 결과가 없습니다.\n\n"
                return

            # context 생성 및 자르기
            context: str = "\n".join([doc.page_content for doc in retrieved_docs])

            def truncate_context(context_text: str, max_length: int = settings.MAX_CONTEXT_LENGTH) -> str:
                return context_text[:max_length]

            final_context = truncate_context(context)
            prompt = f"다음 정보를 참고하여 질문에 답해주세요:\n\n{final_context}"

            try:
                response_iter = self.chain.astream({"question_with_context": prompt, "human_question": query})
                buffer = ""
                async for chunk in response_iter:
                    processed_chunk = clean_chunk(chunk)
                    buffer += processed_chunk

                    while "\n" in buffer:
                        newline_index = buffer.find("\n")
                        line = buffer[:newline_index]
                        yield f"data: {line}\n\n"
                        buffer = buffer[newline_index + 1:]

                    await asyncio.sleep(settings.STREAM_DELAY)

                if buffer:
                    yield f"data: {buffer}\n\n"
            except RequestException as e:
                for chunk in await self._handle_error(e, "AI 모델 연결에 실패했습니다. 서버 상태를 확인해주세요."):
                    yield chunk
            except Exception as e:
                for chunk in await self._handle_error(e, "현재 AI 모델 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."):
                    yield chunk
        except Exception as e:
            for chunk in await self._handle_error(e, "알 수 없는 오류가 발생했습니다."):
                yield chunk
        finally:
            yield "data: [DONE]\n\n"

chat_service = ChatService()
