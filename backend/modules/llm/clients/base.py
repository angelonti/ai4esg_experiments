import math
from abc import ABC, abstractmethod
from typing import Generator

from config import config
from modules.answer.schemas import AnsweredCreate
from modules.llm.llm_infos import CONTEXT_SIZE, Model
from modules.embedding.schemas import Embedding
from modules.embedding.service import get_all
from modules.llm.utils import vector_similarity, get_text_embedding
import tiktoken


class LLMClient(ABC):
    prompt: str | None = None

    def __init__(self, model: Model):
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

    async def ask(self, question: str, prompt: str | None = None) -> tuple[
        list[float], AnsweredCreate, Generator[str, None, None], int]:
        self.prompt = prompt
        question_embedding_response = await get_text_embedding(question)
        question_embedding = question_embedding_response.data[0].embedding

        max_embedding_cnt = self.get_max_embedding_cnt()
        embeddings = self.get_relevant_embeddings(question_embedding, self.get_embeddings(), max_embedding_cnt)

        prompt = self.generate_prompt(question, embeddings)

        num_tokens = len(self.token_encoding.encode(prompt))

        answer_generator = self.get_completion(prompt)

        return question_embedding, AnsweredCreate(answer="", embeddings=embeddings, model=self.model,
                                                  question=question), answer_generator, num_tokens

    @abstractmethod
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        pass

    @staticmethod
    def get_relevant_embeddings(question_embedding: list[float], all_embeddings: list[Embedding], max_num: int) -> list[
        Embedding]:
        return sorted(all_embeddings, reverse=True, key=lambda x: vector_similarity(x.values, question_embedding))[
               :max_num]

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
