from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DocType(Enum):
    PDF = "pdf"
    HTML = "html"
    Website = "website"

class DocumentBase(BaseModel):
    source: str | None

    class Config:
        from_attributes = True

class DocumentParsed(DocumentBase):
    title: str
    text: str
    doc_type: DocType

class Document(DocumentParsed):
    id: UUID
