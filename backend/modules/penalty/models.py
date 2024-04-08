from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base

__all__ = ["PenaltyModel", "PenaltySummaryModel"]


class PenaltyModel(Base):
    __tablename__ = "penalties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    text = Column(String)
    page_number = Column(Integer, default=0)
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,penalties")


class PenaltySummaryModel(Base):
    __tablename__ = "penalty_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    summary = Column(String)
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,penalty_summaries")
