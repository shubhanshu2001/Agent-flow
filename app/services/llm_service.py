# app/services/llm_service.py
from openai import OpenAI
from groq import Groq
from app.core.config import get_settings

settings = get_settings()

# Using Groq free api for testing & developent!

# client = OpenAI(api_key=settings.openai_api_key)
client = Groq(api_key=settings.groq_api_key)

async def generate_llm_response(messages: list[dict]) -> str:
    """
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "..."},
        ...
    ]
    """
    try:
        completion = client.chat.completions.create(
            # model="gpt-4o-mini",
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, I couldn't generate a response."
