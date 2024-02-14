import os
import secrets

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Config:
    def __init__(self):
        self.api_type: str = os.getenv("API_TYPE", "azure")
        self.api_key: str = os.getenv("API_KEY", "insert your OpenAI api key here")
        self.embed_api_key: str = os.getenv("EMBED_API_KEY", "insert your OpenAI embedding api key here")
        self.api_endpoint: str = os.getenv("API_ENDPOINT", "insert your OpenAI api endpoint here")
        self.gpt4_deployment_name: str = os.getenv("GPT4_DEPLOYMENT_NAME", "insert your OpenAI GPT4 deployment name "
                                                                           "here")
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", 1024))
        self.overlap_size: int = int(os.getenv("OVERLAP_SIZE", 256))
        self.max_content: int = int(os.getenv("MAX_CONTENT", 5))
        self.prompt_size: int = int(os.getenv("PROMPT_SIZE", 5000))
        self.add_title: bool = bool(os.getenv("ADD_TITLE", True))
        self.answer_do_not_know: bool = bool(os.getenv("ANSWER_DO_NOT_KNOW", False))
        self.temperature: float = float(os.getenv("TEMPERATURE", 0.0001))

        self.db_user: str = os.getenv("DB_USER", "postgres")
        self.db_pass: str = os.getenv("DB_PASS", "postgres")
        self.db_host: str = os.getenv("DB_HOST", "localhost")
        self.db_port: str = os.getenv("DB_PORT", "5432")
        self.db_name: str = os.getenv("DB_NAME", "ai4esg")


config = Config()
