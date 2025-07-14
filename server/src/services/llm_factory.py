
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI # 예시: OpenAI 모델을 위한 주석 처리

from src.config import settings

def get_llm() -> BaseChatModel:
    """
    설정에 따라 적절한 LLM 클라이언트를 반환합니다.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama":
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
        )
    # elif provider == "openai":
    #     return ChatOpenAI(
    #         model_name=settings.OPENAI_MODEL_NAME,
    #         api_key=settings.OPENAI_API_KEY,
    #         temperature=0.2,
    #     )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

