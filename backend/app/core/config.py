from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "creator_videos"
    cors_origins: str = "http://localhost:3000"
    chunk_size: int = 512
    chunk_overlap: int = 50
    llm_model: str = "llama-3.1-8b-instant"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()