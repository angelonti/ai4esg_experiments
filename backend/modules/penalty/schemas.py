from uuid import UUID

from pydantic import BaseModel

from modules.document.schemas import Document


class PenaltySummaryBase(BaseModel):
    document_id: UUID
    summary: str

    class Config:
        from_attributes = True


class PenaltySummaryCreate(PenaltySummaryBase):
    pass


class PenaltySummary(PenaltySummaryBase):
    id: UUID
    document: Document


class PenaltyBase(BaseModel):
    document_id: UUID
    text: str
    page_number: int = 0

    class Config:
        from_attributes = True


class PenaltyCreate(PenaltyBase):
    pass


class Penalty(PenaltyBase):
    id: UUID
    document: Document
