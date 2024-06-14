from typing import Generator
import sys
import logging

from fastapi import HTTPException
from db.engine import db
from config import config

from modules.answer.models import AnswerModel
from modules.answer.schemas import AnswerCreate
from modules.embedding.schemas import Embedding
from modules.embedding.utils import to_relevant_embeddings
from modules.llm.llm_infos import Model
from modules.embedding.models import EmbeddingModel
from modules.llm.clients.openai.openai_client import OpenAILLMClient
from modules.llm.clients.openai.azure_openai_client import AzureOpenAILLMClient
from modules.llm.clients.open_source.local_llm_client import LocalLLMClient
import time

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


MODEL_MAPPING = {
    Model.Gpt3: lambda: OpenAILLMClient(model=Model.Gpt3),
    Model.Gpt4: lambda: OpenAILLMClient(model=Model.Gpt4),
    Model.AZURE_GPT4: lambda: AzureOpenAILLMClient(model=Model.AZURE_GPT4),
    Model.Mistral: lambda: LocalLLMClient(model=Model.Mistral),
    Model.Mixtral: lambda: LocalLLMClient(model=Model.Mixtral),
    Model.Fusion_Net: lambda: LocalLLMClient(model=Model.Fusion_Net),
}


async def create(request: AnswerCreate, title: str = None) -> tuple[list[float], list[Embedding], Generator[str, None, None], int]:
    try:
        logger.info(f"Creating answer for model: {request.model}")
        llm_client = MODEL_MAPPING[request.model]()
    except KeyError:
        raise HTTPException(status_code=400, detail="Unknown model selected.")

    logger.info(f"Requesting answer for question: {request.question} and prompt: {request.prompt}")
    question_embedding, answer_embeddings, answer_generator, num_tokens = await llm_client.ask(
        request.question, request.prompt, title=title
    )

    # Create AnswerModel
    answer_dict = answer_embeddings.dict()
    embeddings = answer_dict.pop("embeddings")
    answer_obj = AnswerModel(**answer_dict)

    # Convert and add Embeddings
    for embedding in embeddings:
        with db.session.no_autoflush:
            embedding_obj = (
                db.session.query(EmbeddingModel)  # type: ignore
                .filter(EmbeddingModel.id == embedding["id"])
                .first()
            )
            if not embedding_obj:
                raise HTTPException(status_code=400, detail="Unknown embedding used.")
            answer_obj.embeddings.append(embedding_obj)

    # Store initial answer
    db.session.add(answer_obj)
    db.session.commit()
    db.session.refresh(answer_obj)

    # Start streaming
    start = next(answer_generator)

    def generator_wrapper():
        text_latest = start
        yield start
        for text in answer_generator:
            text_latest += text
            time.sleep(0.05)
            yield text

        answer_obj.answer = text_latest
        db.session.add(answer_obj)
        db.session.commit()

    # return question_embedding, Answer.from_orm(answer_obj), generator_wrapper()
    relevant_embeddings = to_relevant_embeddings(question_embedding,answer_embeddings.embeddings)

    return question_embedding, relevant_embeddings, generator_wrapper(), num_tokens