from abc import ABC, abstractmethod
from typing import Any

from langchain import HuggingFacePipeline


class LLM(ABC):
    model: str
    tokenizer: Any

    @abstractmethod
    def get_llm(self) -> HuggingFacePipeline:
        pass
