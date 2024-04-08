from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base


class RequirementModel(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    text = Column(String)
    page_number = Column(Integer, default=0)
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,penalties")

class RequirementSummaryModel(Base):
    __tablename__ = "requirement_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    summary = Column(String)
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,requirement_summaries")
