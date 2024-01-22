from typing import Generator

import openai

from modules.llm.clients.base import LLMClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)


class OpenAILLMClient(LLMClient):
    def fill_dict(self, dst: dict, chunk: dict):
        for key in chunk:
            if chunk[key] is None:
                dst[key] = None
            elif isinstance(chunk[key], dict):
                if key not in dst:
                    dst[key] = {}
                self.fill_dict(dst[key], chunk[key])
            elif isinstance(chunk[key], str):
                if key not in dst:
                    dst[key] = ""
                dst[key] += chunk[key]
            else:
                raise ValueError(f"Unsupported type {type(chunk[key])}")

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        chunk_generator = openai.ChatCompletion.create(
            model=self.model.value,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that can truthfully answer questions using "
                                              "contexts, if the information is there."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        response = {}
        for chunk_all in chunk_generator:
            chunk = chunk_all["choices"][0]["delta"]
            self.fill_dict(response, chunk)
            yield response["content"]

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(6))
    def get_completion_azure(self, prompt: str) -> Generator[str, None, None]:
        chunk_generator = openai.ChatCompletion.create(
            engine=self.model.value,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that can truthfully answer questions using "
                                              "contexts, if the information is there."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        response = {}
        for chunk_all in chunk_generator:
            if "content" in chunk_all["choices"][0]["delta"]:
                chunk = chunk_all["choices"][0]["delta"]
                self.fill_dict(response, chunk)
                yield response["content"]