from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client import models
from sentence_transformers import SentenceTransformer
import uuid
import os

def embed_data_to_qdrant(file_path: str = "data/seoul_info.txt", collection_name: str = "seoul_info") -> None:
    # Qdrant 클라이언트 연결
    client = QdrantClient(host="localhost", port=6333)

    # 콜렉션이 없으면 생성
    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        # text 필드에 대한 인덱스 생성
        client.create_payload_index(
            collection_name=collection_name,
            field_name="text",
            field_type="text",
        )
    else:
        print(f"Collection '{collection_name}' already exists. Skipping creation.")

    # 텍스트 불러오기
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
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

    print(f"✅ Qdrant에 {len(points)}개의 문장 벡터 업로드 완료!")


# 이 파일이 직접 실행될 때만 임베딩을 수행 (선택 사항)
if __name__ == "__main__":
    embed_data_to_qdrant()
