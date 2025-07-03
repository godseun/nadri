import asyncio
from typing import AsyncGenerator

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableGenerator

from src.config import settings

class ChatService:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embedding_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.llm = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 서울에 대한 정보를 잘 알고 있는 AI입니다."),
            ("system", "응답은 간결하고 명확하게 작성해주세요."),
            ("system", "응답은 한국어로 작성해주세요."),
            ("system", "모르면 모른다고 답해주세요."),
            ("user", "{question_with_context}")
        ])
        self.chain: RunnableGenerator[str, str] = self.prompt_template | self.llm | StrOutputParser()

    async def q(self, query: str) -> AsyncGenerator[str, None]:
        # Qdrant에서 검색
        query_vector = self.embedding_model.encode(query).tolist()
        search_result = self.qdrant_client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=5
        )

        # context 자르기
        tokenizer = self.embedding_model._first_module().tokenizer
        context = "\n".join([r.payload["text"] for r in search_result])

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
        prompt = f"다음 정보를 참고하여 질문에 답해주세요:\n\n{final_context}\n\n질문: {query}"

        response_iter = self.chain.stream({"question_with_context": prompt})

        for chunk in response_iter:
            if chunk.strip():
                yield f"data: {chunk.strip()}\n\n"
                await asyncio.sleep(settings.STREAM_DELAY)

        yield "data: [DONE]\n\n"

chat_service = ChatService()
