import asyncio

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Qdrant 연결
client = QdrantClient(host="localhost", port=6333)
collection_name = "seoul_info"

# 임베딩 모델
model = SentenceTransformer("intfloat/multilingual-e5-base")

# LLM (Ollama LangChain wrapper)
llm = ChatOllama(
    model="phi4-mini",
    base_url="http://192.168.219.111:11434",
    temperature=0.2,
)

# LangChain Prompt 구성
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "당신은 서울에 대한 정보를 잘 알고 있는 AI입니다."),
    ("system", "응답은 간결하고 명확하게 작성해주세요."),
    ("system", "응답은 한국어로 작성해주세요."),
    ("system", "모르면 모른다고 답해주세요."),
    ("user", "{question_with_context}")
])

# 파이프라인 구성
chain = prompt_template | llm | StrOutputParser()

async def q(query):
    # Qdrant에서 검색
    query_vector = model.encode(query).tolist()
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=5
    )

    # context 자르기
    tokenizer = SentenceTransformer("intfloat/multilingual-e5-base")._first_module().tokenizer
    context = "\n".join([r.payload["text"] for r in search_result])

    def truncate_context(context, max_length=512, reserved=64):
        max_context_tokens = max_length - reserved
        sentences = context.split("\n")
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

    # LangChain의 .stream()은 async generator를 지원하지 않으므로 수동 처리
    response_iter = chain.stream({"question_with_context": prompt})

    for chunk in response_iter:
        if chunk.strip():
            yield f"data: {chunk.strip()}\n\n"
            await asyncio.sleep(0.05)  # 타자 효과 속도 조절

    yield "data: [DONE]\n\n"