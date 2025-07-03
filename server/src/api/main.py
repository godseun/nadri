from typing import Dict
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from src.services.chat_service import chat_service


app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


@app.post("/chat")
async def chat(payload: Dict[str, str]):
    prompt = payload.get("prompt")
    if not prompt:
        return {"error": "Prompt not found in request"}
    print(f"Received prompt: {prompt}")
    # Qdrant에서 검색하고 스트리밍 응답 반환
    return StreamingResponse(
        chat_service.q(prompt),
        media_type="text/event-stream"
    )
