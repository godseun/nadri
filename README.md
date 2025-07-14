#  프로젝트 나드리 (Nadeuri)

**LLM 기반 국내 여행 정보 챗봇**

---

## 📝 개요

**나드리**는 국내의 다양한 행사, 축제, 여행 정보를 대화형으로 쉽게 탐색할 수 있는 LLM 기반 챗봇 서비스입니다. 사용자는 마치 ChatGPT와 대화하듯 자연어 질의를 통해 원하는 정보를 얻을 수 있습니다.

이 프로젝트는 최신 정보를 제공하기 위해 RAG(Retrieval-Augmented Generation) 아키텍처를 활용합니다. 자체적으로 수집한 국내 여행 관련 데이터를 기반으로 LLM이 답변을 생성하여, 보다 정확하고 신뢰도 높은 정보를 제공하는 것을 목표로 합니다.

## ✨ 주요 기능

- **대화형 정보 검색**: 자연어 질의를 통해 국내 행사, 축제, 명소 정보 검색
- **RAG 기반 답변 생성**: 자체 DB 기반으로 환각(Hallucination)을 최소화한 정확한 정보 제공
- **사용자 친화적 인터페이스**: 직관적인 채팅 UI 제공
- **테마 지원**: 라이트/다크 모드 전환 기능

## 🛠️ 기술 스택

| 구분      | 기술                               |
| :-------- | :--------------------------------- |
| **Frontend** | React, TypeScript, SCSS     |
| **Backend**  | Python, FastAPI, Poetry, LangChain |
| **LLM**      | Ollama, phi4-mini               |
| **Database** | qdrant (Vector)           |

## 📂 프로젝트 구조

```
gemini-agent-api/
├── frontend/       # React 기반 프론트엔드
│   ├── src/
│   └── package.json
└── server/         # Python 기반 백엔드
    ├── src/
    │   ├── api/      # FastAPI 라우터
    │   ├── services/ # 비즈니스 로직 (채팅, 데이터 처리)
    │   ├── prompts/  # LLM 프롬프트 관리
    │   └── data/     # 원본 데이터
    └── pyproject.toml
```

## 🚀 설치 및 실행 방법

### 1. Backend (Server)

```bash
# 1. 서버 디렉토리로 이동
cd server

# 2. Poetry를 사용하여 의존성 설치
poetry install

# 3. .env 파일 설정
#    - .env.example 파일을 복사하여 .env 파일 생성
#    - OPENAI_API_KEY 등 필요한 환경 변수 설정
cp .env.example .env
# nano .env

# 4. (최초 실행 시) 데이터 임베딩
#    - data/ 디렉토리에 있는 정보를 기반으로 Vector DB를 생성합니다.
poetry run python src/services/embed_data.py

# 5. 서버 실행 (FastAPI)
poetry run uvicorn src.api.main:app --reload
```

### 2. Frontend (Client)

```bash
# 1. 프론트엔드 디렉토리로 이동
cd frontend

# 2. NPM을 사용하여 의존성 설치
npm install

# 3. .env 파일 설정
#    - .env.example 파일을 복사하여 .env 파일 생성
#    - REACT_APP_API_URL 등 백엔드 서버 주소 설정
cp .env.example .env
# nano .env

# 4. 프론트엔드 개발 서버 실행
npm start
```

---
