from src.services.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM (Ollama LangChain wrapper)
llm = get_llm()

# LangChain Prompt 구성
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "당신은 서울에 대한 정보를 잘 알고 있는 AI입니다."),
    ("system", "응답은 간결하고 명확하게 작성해주세요."),
    ("system", "응답은 한국어로 작성해주세요."),
    ("system", "모르면 모른다고 답해주세요."),
    ("user", "{question_with_context}")
])

# 파이프라인 구성
chain = prompt_template | llm | StrOutputParser()

q = chain.invoke({
    "question_with_context": "대구 날씨 어때?"
})

print(q)