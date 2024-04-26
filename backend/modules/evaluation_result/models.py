from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base import Base


class EvaluationResultModel(Base):
    __tablename__ = "evaluation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    evaluation_name = Column(String)
    evaluation = Column(JSONB)
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,evaluation_results")