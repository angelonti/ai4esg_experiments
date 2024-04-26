from uuid import UUID

from pydantic import BaseModel

from modules.document.schemas import Document


class EvaluationResultBase(BaseModel):
    document_id: UUID
    evaluation_name: str
    evaluation: dict

    class Config:
        from_attributes = True


class EvaluationResultCreate(EvaluationResultBase):
    pass


class EvaluationResult(EvaluationResultBase):
    id: UUID
    document: Document
