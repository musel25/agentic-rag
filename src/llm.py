# from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI

# def get_llm(temperature: float = 0.0) -> ChatDeepSeek:
#     """Initialize and return the DeepSeek LLM."""
#     return ChatDeepSeek(
#         model="deepseek-chat", 
#         temperature=temperature
#     )


def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Initialize and return the Gemini Flash LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=temperature,
        max_retries=2
    )
