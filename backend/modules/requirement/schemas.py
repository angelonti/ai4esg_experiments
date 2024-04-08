from uuid import UUID

from pydantic import BaseModel

from modules.document.schemas import Document


class RequirementSummaryBase(BaseModel):
    document_id: UUID
    summary: str

    class Config:
        from_attributes = True


class RequirementSummaryCreate(RequirementSummaryBase):
    pass


class RequirementSummary(RequirementSummaryBase):
    id: UUID
    document: Document


class RequirementBase(BaseModel):
    document_id: UUID
    text: str
    page_number: int = 0

    class Config:
        from_attributes = True


class RequirementCreate(RequirementBase):
    pass


class Requirement(RequirementBase):
    id: UUID
    document: Document
