import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

print(f"Qdrant 연결 시도 중: {QDRANT_HOST}:{QDRANT_PORT}")

try:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    # 간단한 헬스 체크 (컬렉션 목록 가져오기)
    collections = client.get_collections()
    print("Qdrant 서버에 성공적으로 연결되었습니다.")
    print(f"현재 컬렉션: {collections.collections}")
except Exception as e:
    print(f"Qdrant 서버 연결 실패: {e}")
