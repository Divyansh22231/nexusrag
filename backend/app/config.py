from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "nexusrag"
    
    RAG_CANDIDATE_K: int = 8
    RAG_TOP_K: int = 4
    RAG_SCORE_THRESHOLD: float = 0.50
    RERANKING_ENABLED: bool = True
    
    FRONTEND_ORIGIN: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
