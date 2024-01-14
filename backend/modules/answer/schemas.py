from uuid import UUID

from pydantic import BaseModel

from modules.embedding.schemas import Embedding
from modules.llm.llm_infos import Model


class AnswerBase(BaseModel):
    question: str
    model: Model

    class Config:
        orm_mode = True


class AnswerCreate(AnswerBase):
    prompt: str | None = None
    pass


class AnsweredCreate(AnswerBase):
    answer: str
    embeddings: list[Embedding]


class Answer(AnsweredCreate):
    id: UUID
