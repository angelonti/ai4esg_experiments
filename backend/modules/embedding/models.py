from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY, Float

from db.base import Base
from modules.answer.models import answer_embeddings


class EmbeddingModel(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,embeddings")
    values = Column(ARRAY(Float))
    size = Column(Integer)
    offset = Column(Integer)
    answers = relationship("AnswerModel", back_populates="embeddings", secondary=answer_embeddings, cascade="all,delete")