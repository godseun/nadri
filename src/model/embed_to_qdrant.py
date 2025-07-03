from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# Qdrant 클라이언트 연결
client = QdrantClient(host="localhost", port=6333)

# 콜렉션 생성 (한 번만 실행되면 됨)
collection_name = "seoul_info"

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# 텍스트 불러오기
with open("seoul_info.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

chunks = [chunk.strip() for chunk in raw_text.split("\n") if chunk.strip()]

# 임베딩
model = SentenceTransformer("intfloat/multilingual-e5-base")
embeddings = model.encode(chunks)

# Qdrant에 데이터 업로드
points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=vector.tolist(),
        payload={"text": text},
    )
    for vector, text in zip(embeddings, chunks)
]

client.upsert(collection_name=collection_name, points=points)

print("✅ Qdrant에 문장 벡터 업로드 완료!")