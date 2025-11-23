from pydantic import BaseModel

class Settings(BaseModel):
    ollama_url: str = "http://localhost:11434/api/generate"
    model_name: str = "qwen2.5:7b"
    secret_key: str = "change-me-super-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
