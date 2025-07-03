import asyncio

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from transformers import pipeline, AutoTokenizer

# Qdrant 연결
client = QdrantClient(host="localhost", port=6333)
collection_name = "seoul_info"

# 임베딩 모델 로드 (업로드할 때와 동일한 모델 써야 함)
model = SentenceTransformer("intfloat/multilingual-e5-base")

# --- LLM 기반 RAG 답변 생성 ---
# LLM 준비 (예: HuggingFace Transformers 기반)
rag_pipeline = pipeline(
    # "text2text-generation",
    "text-generation",
    model="microsoft/Phi-4-mini-instruct",  # 또는 원하는 LLM으로 교체
    tokenizer="microsoft/Phi-4-mini-instruct",
    # device=-1
)

async def q(query):
    # 질의 벡터화
    query_vector = model.encode(query).tolist()
    # Qdrant에서 검색
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=5  # 상위 5개 검색
    )

    print(f"검색된 문단 수: {len(search_result)}")
    # --- context 길이 제한 로직 추가 ---
    # 토크나이저 준비
    tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")

    # 검색된 문단들을 context로 결합
    context = "\n".join([r.payload["text"] for r in search_result])

    # context 자르기
    def truncate_context(context, max_length=512, reserved_for_prompt=64):
        prompt_prefix = "다음 정보를 바탕으로 질문에 답해주세요:\n\n"
        prompt_suffix = f"\n\n질문: {query}\n답변:"
        max_context_tokens = max_length - reserved_for_prompt

        sentences = context.split("\n")
        final_context = []
        total_tokens = 0
        for sentence in sentences:
            tokens = tokenizer.encode(sentence, add_special_tokens=False)
            if total_tokens + len(tokens) > max_context_tokens:
                break
            final_context.append(sentence)
            total_tokens += len(tokens)
        return "\n".join(final_context), prompt_prefix, prompt_suffix

    # context 자르기 적용
    context, prefix, suffix = truncate_context(context)
    prompt = f"{prefix}{context}{suffix}"

    output = rag_pipeline(
        prompt, 
        max_new_tokens=512,
        return_full_text=False,
        do_sample=False
    )[0]
    # 생성 결과 분할
    full_text = output.get("generated_text", output.get("text", "⚠️ 응답 없음"))
    for sentence in full_text.split(". "):  # 간단한 문장 단위 나눔
        if sentence.strip():
            yield f"data: {sentence.strip()}.\n\n"
            await asyncio.sleep(0.2)  # 약간의 딜레이로 스트리밍 느낌

    yield "data: [DONE]\n\n"