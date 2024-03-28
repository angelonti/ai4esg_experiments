from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base
from modules.answer.models import answer_embeddings


class EmbeddingModel(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    document = relationship("DocumentModel", foreign_keys=[document_id], overlaps="documents,embeddings")
    values = Column(Vector(1536))
    size = Column(Integer)
    offset = Column(Integer)
    page_number = Column(Integer, default=0)
    answers = relationship("AnswerModel", back_populates="embeddings", secondary=answer_embeddings, cascade="all,delete")