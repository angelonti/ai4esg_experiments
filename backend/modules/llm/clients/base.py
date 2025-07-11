import math
from abc import ABC, abstractmethod
from typing import Generator

from app_config import config
from modules.answer.schemas import AnsweredCreate
from modules.llm.llm_infos import CONTEXT_SIZE, Model
from modules.embedding.schemas import Embedding
from modules.embedding.service import get_all, get_similar, get_similar_hybrid
from modules.embedding.utils import to_relevant_embeddings
from modules.llm.utils import get_text_embedding
import tiktoken


class LLMClient(ABC):
    prompt: str | None = None

    def __init__(self, model: Model = Model.AZURE_GPT4):
        self.model = model
        self.token_encoding = tiktoken.get_encoding("cl100k_base")
        self.default_prompt = self.get_default_prompt()
        self.priming = """You are a helpful assistant and legal expert that can
         answer questions, you always answer by copying exactly an excerpt of the provided contexts"""

    @staticmethod
    def get_default_prompt() -> str:
        if config.answer_do_not_know:
            default_prompt = '''Answer the question as truthfully as possible using the provided contexts, "
            "and if the answer is not contained within the text in the contexts, say `I don't know.`'''
        else:
            default_prompt = '''Answer the question as truthfully as possible using the provided contexts.'''

        return default_prompt

    async def ask(self, question: str, prompt: str | None = None, title: str = None) \
            -> tuple[list[float], AnsweredCreate, Generator[str, None, None], int, list[dict]]:
        self.prompt = prompt
        question_embedding_response = await get_text_embedding(question)
        question_embedding: list[float] = question_embedding_response.data[0].embedding

        max_embedding_cnt = self.get_max_embedding_cnt()
        # Refactor later. Now easier to test like this
        if config.use_hybrid:
            print(f"###### using hybrid search")
            embeddings_with_scores = self.get_relevant_embeddings_hybrid(question, question_embedding, max_embedding_cnt, title=title)
            print(f"got {len(embeddings_with_scores)} embeddings with scores.")
        else:
            print(f"###### using regular search")
            embeddings_with_scores = self.get_relevant_embeddings(question_embedding, max_embedding_cnt, title=title)

        embeddings = [embedding for embedding, _ in embeddings_with_scores]
        prompt = self.generate_prompt(question, embeddings)

        num_tokens = len(self.token_encoding.encode(prompt))
        # print(f"##### the full prompt is: {prompt}")
        answer_generator = self.get_completion(prompt)

        relevant_embeddings = to_relevant_embeddings(embeddings_with_scores)

        return (
                question_embedding,
                AnsweredCreate(answer="", embeddings=embeddings, model=self.model, question=question),
                answer_generator,
                num_tokens,
                relevant_embeddings
        )

    @abstractmethod
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        pass

    @staticmethod
    def get_relevant_embeddings(question_embedding: list[float], max_num: int, title: str = None) -> list[tuple[Embedding, float]]:
        return get_similar(question_embedding, max_num, title=title)

    @staticmethod
    def get_relevant_embeddings_hybrid(query: str, question_embedding: list[float], max_num: int, title: str = None) -> list[tuple[Embedding, float]]:
        return get_similar_hybrid(query, question_embedding, max_num, title=title)

    def generate_prompt(self, question: str, embeddings: list[Embedding]) -> str:
        if self.prompt:
            return f"{self.prompt}\nContexts: {self.generate_context_string(embeddings)}\nQuestion: {question}\nAnswer:"

        return (
            f"{self.default_prompt} \nContexts: {self.generate_context_string(embeddings)} \nQuestion: {question}\nAnswer:"
        )

    @staticmethod
    def generate_context_string(embeddings: list[Embedding]) -> str:
        if config.add_title:
            return "\n\n".join([f"title:{embedding.document.title}\n{embedding.text}" for embedding in embeddings])

        return "\n\n".join([f"{embedding.text}" for embedding in embeddings])

    @staticmethod
    def get_embeddings() -> list[Embedding]:
        return get_all()

    def get_max_embedding_cnt(self) -> int:
        max_possible = math.floor(
            (CONTEXT_SIZE[self.model] * 4 - config.prompt_size) / config.chunk_size
        )
        return min(max_possible, config.max_content)
