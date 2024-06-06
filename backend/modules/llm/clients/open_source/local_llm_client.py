import logging
import sys
import time
from typing import Generator

from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

from config import config
from modules.llm.clients.base import LLMClient
from modules.llm.clients.openai.utils import streamed_content_generator
from modules.llm.llm_infos import ModelType

logging.basicConfig(level=logging.DEBUG, filename="ai4esg.log", format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


class LocalLLMClient(LLMClient):

    MODEL_TYPE_MAPPING = {
        "mistral": ModelType.GGUF,
        "mixtral": ModelType.GPTQ,
        "fusion_net": ModelType.GGUF
    }

    def __init__(self, model):
        super().__init__(model)
        self.gptq_model = None

    @retry(wait=wait_random_exponential(min=5, max=20), stop=stop_after_attempt(6))
    def get_completion(self, prompt: str) -> Generator[str, None, None]:
        model_type = self.MODEL_TYPE_MAPPING[self.model.value]
        if model_type == ModelType.GGUF:
            return self.get_completion_gguf(prompt)
        raise ValueError(f"Model type {model_type} not supported")

    def get_completion_gguf(self, prompt) -> Generator[str, None, None]:
        start = time.time()
        client = OpenAI(base_url=config.api_endpoint, api_key=config.openai_api_key)
        try:
            output = client.chat.completions.create(
                model=self.model.value,
                messages=[
                    {"role": "system", "content": self.priming},
                    {"role": "user", "content": prompt},
                ],
                temperature=config.temperature,
                stream=True
            )
        except Exception as e:
            logger.error(f"Error in openai completion: {e.__str__()}")
            raise e

        logger.debug(f"Time: {time.time() - start}")
        return streamed_content_generator(output)

    @staticmethod
    def clean_output(output: str) -> str:
        return output.replace("[INST]", "").replace("[/INST]", "")
