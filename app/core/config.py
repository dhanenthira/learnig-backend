from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeArena API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "codearena_super_secret_jwt_key_development_2026_x89f!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = ""
    USE_MOCK_FIREBASE: bool = True
    
    # Code Execution Sandbox
    SANDBOX_TIMEOUT_SECONDS: int = 5
    SANDBOX_MAX_MEMORY_MB: int = 256
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
