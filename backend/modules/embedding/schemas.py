from uuid import UUID

from pydantic import BaseModel

from modules.document.schemas import Document


class EmbeddingBase(BaseModel):
    document_id: UUID
    values: list[float]
    size: int
    offset: int
    page_number: int = 0

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class EmbeddingCreate(EmbeddingBase):
    pass


class Embedding(EmbeddingBase):
    id: UUID
    document: Document

    @property
    def text(self):
        return self.document.text[self.offset: self.offset + self.size]
