from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Syllabus Parser"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./syllabus_parser.db"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # File uploads
    upload_dir: Path = Path("uploads")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".pdf", ".docx", ".doc", ".txt"}

    class Config:
        env_file = ".env"


settings = Settings()
