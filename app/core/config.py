# app/core/config.py
from pydantic import BaseModel
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env

class Settings(BaseModel):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    openai_api_key: str | None = None
    groq_api_key: str | None = None
    tavily_api_key: str | None = None

    class Config:
        frozen = True  # make it immutable

@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL"),
        secret_key=os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
