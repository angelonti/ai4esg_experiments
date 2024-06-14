from typing import Generator
from config import config
import logging
import sys

from openai import OpenAI

from modules.llm.clients.base import LLMClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)

from modules.llm.clients.openai.utils import streamed_content_generator

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

client = OpenAI(
    api_key=config.openai_api_key,
)


class OpenAILLMClient(LLMClient):

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        chunk_generator = client.chat.completions.create(model=self.model.value,
                                                         messages=[
                                                             {"role": "system", "content": self.priming},
                                                             {"role": "user", "content": prompt},
                                                         ],
                                                         temperature=config.temperature,
                                                         stream=True)
        return streamed_content_generator(chunk_generator)
