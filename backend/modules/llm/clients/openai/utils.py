from typing import Generator

from openai import Stream
from openai.types.chat import ChatCompletionChunk
from app_config import config
import logging
import sys

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


def streamed_content_generator(chunk_generator: Stream[ChatCompletionChunk]) -> Generator[str, None, None]:
    response = {"content": ""}
    for chunk_all in chunk_generator:
        # print(f"### chunk_all.choices is {chunk_all.choices}")
        # print(f"### chunk_all is {chunk_all}")
        if not chunk_all.choices:
            continue

        delta = chunk_all.choices[0].delta
        if delta.content:
            response["content"] = delta.content
            yield response["content"]