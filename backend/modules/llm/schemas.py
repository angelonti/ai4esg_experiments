from pydantic import BaseModel


class EmbeddingResponseData(BaseModel):
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    data: list[EmbeddingResponseData]
