import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("demo.env"))


class Config:
    def __init__(self):
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "insert your OpenAI api key here")
        self.azure_openai_key: str = os.getenv("AZURE_OPENAI_KEY", "insert your OpenAI embedding api key here")
        self.api_endpoint: str = os.getenv("API_ENDPOINT", "insert your OpenAI api endpoint here")
        self.api_version: str = os.getenv("API_VERSION", "2023-05-15")
        self.azure_gpt4_deployment_name: str = os.getenv("AZURE_GPT4_DEPLOYMENT_NAME", "insert your OpenAI GPT4 deployment name here")
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", 1024))
        self.overlap_size: int = int(os.getenv("OVERLAP_SIZE", 256))
        self.max_content: int = int(os.getenv("MAX_CONTENT", 5))
        self.prompt_size: int = int(os.getenv("PROMPT_SIZE", 5000))
        self.add_title: bool = bool(os.getenv("ADD_TITLE", False))
        self.answer_do_not_know: bool = bool(os.getenv("ANSWER_DO_NOT_KNOW", False))
        self.temperature: float = float(os.getenv("TEMPERATURE", 0.0001))
        #TODO: might need to add to env file later
        self.use_hybrid: bool = bool(os.getenv("USE_HYBRID", True))
        self.use_reranking: bool = bool(os.getenv("USE_RERANKING", False))
        self.hybrid_fusion: str = os.getenv("HYBRID_FUSION", "reciprocal_rank")

        self.db_user: str = os.getenv("DB_USER", "postgres")
        self.db_pass: str = os.getenv("DB_PASS", "postgres")
        self.db_host: str = os.getenv("DB_HOST", "localhost")
        self.db_port: str = os.getenv("DB_PORT", "5432")
        self.db_name: str = os.getenv("DB_NAME", "ai4esg")
        self.app_path: str = os.getenv("APP_PATH", "http://localhost:8501")
        self.log_path: str = os.getenv("LOG_PATH", "ai4esg.log")
        print("connecting to database: ", self.db_host, self.db_port, self.db_name)
        print("log path: ", self.log_path)


config = Config()

