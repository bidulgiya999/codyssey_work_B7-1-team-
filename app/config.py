from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """.env 파일 또는 환경 변수에서 읽는 앱 설정."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # B: 세션 서명·SQLite 연결
    SECRET_KEY: str = Field(min_length=16)
    DATABASE_URL: str = "sqlite:///./app.db"

    # C: Groq 서버 전용 API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_TIMEOUT_SECONDS: float = Field(default=30, gt=0)
    GROQ_MAX_COMPLETION_TOKENS: int = Field(default=6000, ge=128, le=16000)

    # Reels: 교육용 NC 자료는 상업용 scope에서 검색되지 않는다.
    KNOWLEDGE_USAGE_SCOPE: str = "educational_noncommercial"
    SESSION_HTTPS_ONLY: bool = False
    ENABLE_API_DOCS: bool = False
    CHAT_TOTAL_TIMEOUT_SECONDS: float = Field(default=40, gt=0, le=120)


settings = Settings()
