import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Config:
    api_key: str = os.getenv("API_KEY", "insert your OpenAI api key here")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 1024))
    overlap_size: int = int(os.getenv("OVERLAP_SIZE", 256))
    max_content: int = int(os.getenv("MAX_CONTENT", 5))
    prompt_size: int = int(os.getenv("PROMPT_SIZE", 5000))
    add_title: bool = bool(os.getenv("ADD_TITLE", True))

    db_user: str = os.getenv("DB_USER", "postgres")
    db_pass: str = os.getenv("DB_PASS", "postgres")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "ai4esg")


config = Config()
