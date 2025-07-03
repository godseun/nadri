from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.model import search_in_qdrant


app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Chat</h1>
        <div id="loading" style="display:none; color: gray;">답변 생성 중...</div>
        <input type="text" id="messageText" autocomplete="off" />
        <button id="sendBtn">Send</button>
        <ul id='messages'>
        </ul>
        <script>

            window.onload = () => {

                const input = document.getElementById("messageText");
                const button = document.getElementById("sendBtn");
                const loading = document.getElementById("loading");

                async function sendMessage(event) {
                    event.preventDefault()


                    if (input.value === '') return

                    input.disabled = true;
                    button.disabled = true;
                    loading.style.display = "block";

                    const userMessage = input.value
                    
                    // 화면에 질문 표시
                    const messages = document.getElementById('messages')
                    const userBubble = document.createElement('li')
                    userBubble.textContent = 'Q : ' + userMessage
                    messages.appendChild(userBubble)

                    try {
                        // fetch with streaming response
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: userMessage })
                        })

                        if (!response.ok) {
                            const errorText = await response.text()
                            console.error('Error:', errorText)
                            return
                        }

                        const reader = response.body.getReader()
                        const decoder = new TextDecoder()
                        let partial = ''
                        let botBubble = document.createElement('li')
                        messages.appendChild(botBubble)

                        while (true) {
                            const { done, value } = await reader.read()
                            if (done) break

                            const chunk = decoder.decode(value, { stream: true })
                            partial += chunk

                            // SSE는 "data: ..." 형식이므로 줄 단위 파싱
                            const lines = partial.split('\\n\\n')
                            partial = lines.pop()  // 아직 완전하지 않은 조각은 보류

                            for (let line of lines) {
                                if (line.startsWith('data:')) {
                                    const text = line.replace('data: ', '').trim()
                                    if (text === '[DONE]') return

                                    // ⌨️ 타이핑 효과 - 한 글자씩 출력
                                    for (let char of text) {
                                        botBubble.textContent += char
                                        await new Promise(resolve => setTimeout(resolve, 20)) // 속도 조절
                                    }
                                }
                            }
                        }
                    } catch (error) {
                    } finally {
                        input.value = ''  // 입력 필드 비우기

                        input.disabled = false;
                        button.disabled = false;
                        loading.style.display = "none";
                    }
                }
                document.getElementById("sendBtn").addEventListener("click", sendMessage)
            }


        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.post("/chat")
async def chat(payload: dict):
    prompt = payload.get("prompt")
    if not prompt:
        return {"error": "Prompt not found in request"}
    print(f"Received prompt: {prompt}")
    # Qdrant에서 검색하고 스트리밍 응답 반환
    return StreamingResponse(
        search_in_qdrant.q(prompt),
        media_type="text/event-stream"
    )
