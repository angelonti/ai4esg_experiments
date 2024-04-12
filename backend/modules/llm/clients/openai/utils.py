from typing import Generator

from openai import Stream
from openai.types.chat import ChatCompletionChunk
import logging
import sys

logging.basicConfig(level=logging.DEBUG, filename="ai4esg.log", format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


def streamed_content_generator(chunk_generator: Stream[ChatCompletionChunk]) -> Generator[str, None, None]:
    response = {"content": ""}
    for chunk_all in chunk_generator:
        delta = chunk_all.choices[0].delta
        if delta.content:
            response["content"] = delta.content
            yield response["content"]