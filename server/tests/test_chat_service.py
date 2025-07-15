import asyncio
import os
import json
import langchain

langchain.debug = True
from src.services.chat_service import ChatService
from src.config import settings

async def test_chat_service():
    

    chat_service = ChatService()
    
    # 테스트 쿼리
    query = "서울의 유명한 관광지는 어디인가요?"
    print(f"질의: {query}\n")

    try:
        async for chunk in chat_service.q(query):
            # 'data: ' 접두사 제거 및 출력
            if chunk.startswith("data: "):
                content = chunk[len("data: "):].strip()
                if content == "[DONE]":
                    print("\n[스트림 종료]")
                else:
                    try:
                        # JSON 형식의 오류 메시지 파싱 시도
                        error_data = json.loads(content)
                        if error_data.get("type") == "error":
                            print(f'오류: {error_data.get("message")}')
                        else:
                            print(content, end="")
                    except:
                        # JSON 형식이 아니면 그대로 출력
                        print(content, end="")
            else:
                print(chunk, end="")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_service())
