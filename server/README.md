# 백엔드 애플리케이션

이 프로젝트의 백엔드 애플리케이션은 Gemini CLI를 위한 API를 제공하며, 채팅 상호작용 및 데이터 처리를 담당합니다.

## 사용 기술

*   **FastAPI**: Python 3.7+의 표준 타입 힌트를 기반으로 API를 구축하기 위한 현대적이고 빠른(고성능) 웹 프레임워크입니다.
*   **Qdrant**: 벡터 유사성 검색 엔진입니다.
*   **Sentence Transformers**: 최신 문장, 텍스트 및 이미지 임베딩을 위한 Python 프레임워크입니다.
*   **LangChain**: 언어 모델 기반 애플리케이션 개발을 위한 프레임워크입니다.
*   **Ollama**: 로컬에서 대규모 언어 모델을 실행하기 위한 도구입니다.
*   **BeautifulSoup4**: HTML 및 XML 파일에서 데이터를 추출하기 위한 Python 라이브러리입니다.
*   **Requests**: Python을 위한 우아하고 간단한 HTTP 라이브러리입니다.

## 시작하기

백엔드 애플리케이션을 실행하기 위한 단계별 지침입니다.

### 전제 조건

다음 소프트웨어가 시스템에 설치되어 있는지 확인하세요:

*   Python 3.9+
*   Poetry (의존성 관리를 위해)
*   Docker (Qdrant 및 Ollama를 위해)

### 설치

`server` 디렉토리로 이동하여 Poetry를 사용하여 의존성을 설치합니다:

```bash
cd server
poetry install
```

### 환경 변수

이 애플리케이션은 환경 변수를 사용하여 구성됩니다. `server` 디렉토리(`pyproject.toml`이 있는 곳)에 `.env` 파일을 생성하고 다음 변수들을 추가합니다:

```
# server/.env
QDRANT_HOST=localhost
QDRANT_PORT=6333
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi4-mini
SENTENCE_TRANSFORMER_MODEL=intfloat/multilingual-e5-base
QDRANT_COLLECTION_NAME=seoul_info
MAX_CONTEXT_LENGTH=512
RESERVED_TOKENS=64
STREAM_DELAY=0.05
```

*   **`QDRANT_HOST`**: Qdrant 서비스 호스트.
*   **`QDRANT_PORT`**: Qdrant 서비스 포트.
*   **`OLLAMA_BASE_URL`**: Ollama 인스턴스의 기본 URL.
*   **`OLLAMA_MODEL`**: 사용할 Ollama 모델 (예: `phi4-mini`).
*   **`SENTENCE_TRANSFORMER_MODEL`**: 임베딩에 사용할 Sentence Transformer 모델.
*   **`QDRANT_COLLECTION_NAME`**: Qdrant의 컬렉션 이름.
*   **`MAX_CONTEXT_LENGTH`**: 컨텍스트 잘라내기를 위한 최대 토큰 길이.
*   **`RESERVED_TOKENS`**: 컨텍스트 잘라내기에서 프롬프트를 위해 예약된 토큰.
*   **`STREAM_DELAY`**: 스트리밍 응답(타이핑 효과)을 위한 지연 시간(초).

### 종속 서비스 실행 (Qdrant & Ollama)

Qdrant와 Ollama는 Docker를 사용하여 실행하는 것을 권장합니다. 시스템에 Docker가 실행 중인지 확인하세요.

1.  **Qdrant 시작:**

    ```bash
    docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
    ```

2.  **Ollama 시작 및 모델 다운로드 (예: phi4-mini):**

    ```bash
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    docker exec -it ollama ollama pull phi4-mini
    ```

### 데이터 준비 (크롤링 & 임베딩)

채팅 서비스를 실행하기 전에 데이터를 크롤링하고 Qdrant에 임베딩해야 합니다.

1.  **데이터 크롤링:**

    ```bash
    cd server && poetry run python src/services/crawl_seoul.py
    ```

    이 명령은 위키백과에서 데이터를 크롤링하여 `server/data/seoul_info.txt`에 저장합니다.

2.  **Qdrant에 데이터 임베딩:**

    ```bash
    cd server && poetry run python src/services/embed_data.py
    ```

    이 명령은 `seoul_info.txt`를 읽고 임베딩을 생성하여 Qdrant 인스턴스에 업로드합니다.

### 백엔드 애플리케이션 실행

FastAPI 개발 서버를 시작하려면 프로젝트 루트 디렉토리에서 다음 명령을 실행합니다:

```bash
cd server && poetry run uvicorn src.api.main:app --reload
```

API는 `http://localhost:8000`에서 사용할 수 있습니다.

## 프로젝트 구조

*   `server/src/api/`: FastAPI 애플리케이션 진입점 및 API 라우트.
    *   `main.py`: 메인 FastAPI 애플리케이션.
*   `server/src/services/`: 비즈니스 로직 및 외부 서비스(Qdrant, Ollama)와의 상호작용.
    *   `chat_service.py`: 채팅 로직, Qdrant 검색 및 LLM 상호작용을 처리합니다.
    *   `crawl_seoul.py`: 데이터 크롤링 스크립트.
    *   `embed_data.py`: Qdrant에 데이터를 임베딩하는 스크립트.
*   `server/src/config/`: 구성 파일.
    *   `settings.py`: 환경 변수 및 애플리케이션 설정을 관리합니다.
*   `server/data/`: 크롤링된 데이터(예: `seoul_info.txt`)를 저장합니다.