from typing import Generator
from config import config
import logging
import sys
import openai

from openai import AzureOpenAI

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

openai.api_key = config.azure_openai_key
openai.api_base = config.api_endpoint
openai.api_version = "2023-05-15"

azure_client = AzureOpenAI(
    api_key=config.azure_openai_key,
    api_version=config.api_version,
    azure_endpoint=config.api_endpoint
)


class AzureOpenAILLMClient(LLMClient):
    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        logger.debug(f"calling openai API with prompt: \n\n{prompt}\n\n")
        logger.debug(f"calling openai API with temperature {config.temperature}")
        chunk_generator = azure_client.chat.completions.create(model=self.model.value,
                                                               messages=[
                                                                   {"role": "system", "content": self.priming},
                                                                   {"role": "user", "content": prompt},
                                                               ],
                                                               temperature=config.temperature,
                                                               stream=True)
        return streamed_content_generator(chunk_generator)
