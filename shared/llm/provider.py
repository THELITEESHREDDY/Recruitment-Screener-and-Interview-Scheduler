from ..config import settings
from langchain_groq import ChatGroq


llm_service = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    api_key=settings.GROQ_API_AGENTS_PROVIDER
)