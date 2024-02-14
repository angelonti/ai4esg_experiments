from typing import Generator
from config import config
import logging
import sys

from openai import OpenAI, Stream
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionChunk


logging.basicConfig(level=logging.DEBUG, filename="ai4esg.log", format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)

client = OpenAI(
    api_key=config.openai_api_key,
)
azure_client = AzureOpenAI(
    api_key=config.azure_openai_key,
    api_version=config.api_version,
    azure_endpoint=config.api_endpoint
)

from modules.llm.clients.base import LLMClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)


class OpenAILLMClient(LLMClient):

    @staticmethod
    def streamed_content_generator(chunk_generator: Stream[ChatCompletionChunk]) -> Generator[str, None, None]:
        response = {"content": ""}
        for chunk_all in chunk_generator:
            delta = chunk_all.choices[0].delta
            if delta.content:
                response["content"] += delta.content
                yield response["content"]

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        priming = """You are a helpful legal expert in the area of website privacy policies that can
         answer questions, you always answer by copying exactly an excerpt of the contexts"""
        chunk_generator = client.chat.completions.create(model=self.model.value,
                                                         messages=[
                                                             {"role": "system", "content": priming},
                                                             {"role": "user", "content": prompt},
                                                         ],
                                                         stream=True)
        return self.streamed_content_generator(chunk_generator)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion_azure(self, prompt: str) -> Generator[str, None, None]:
        priming = """You are a helpful assistant and legal expert that can
         answer questions, you always answer by copying exactly an excerpt of the contexts"""
        logger.debug(f"calling openai API with prompt: \n\n{prompt}\n\n")
        logger.debug(f"calling openai API with temperature {config.temperature}")
        chunk_generator = azure_client.chat.completions.create(model=self.model.value,
                                                               messages=[
                                                                   {"role": "system", "content": priming},
                                                                   {"role": "user", "content": prompt},
                                                               ],
                                                               temperature=config.temperature,
                                                               stream=True)
        return self.streamed_content_generator(chunk_generator)
