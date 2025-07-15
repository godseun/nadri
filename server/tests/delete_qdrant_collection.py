import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "seoul_info")

print(f"Qdrant 연결 시도 중: {QDRANT_HOST}:{QDRANT_PORT}")

try:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    if client.collection_exists(collection_name=QDRANT_COLLECTION_NAME):
        client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)
        print(f"컬렉션 '{QDRANT_COLLECTION_NAME}' 삭제 완료.")
    else:
        print(f"컬렉션 '{QDRANT_COLLECTION_NAME}'이(가) 존재하지 않습니다. 삭제를 건너뜁니다.")
    
    collections = client.get_collections()
    print(f"현재 컬렉션: {collections.collections}")

except Exception as e:
    print(f"Qdrant 서버 연결 또는 컬렉션 삭제 실패: {e}")
