import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini-reasoning")

# Sentence Transformer 모델 이름
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "intfloat/multilingual-e5-base")

# Qdrant 컬렉션 이름
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "seoul_info")

# 컨텍스트 자르기 설정
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 512))
RESERVED_TOKENS = int(os.getenv("RESERVED_TOKENS", 64))

# 스트리밍 응답 딜레이 (타자 효과)
STREAM_DELAY = float(os.getenv("STREAM_DELAY", 0.05))
