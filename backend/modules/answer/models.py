from uuid import uuid4

from sqlalchemy import Column, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base
from modules.llm.llm_infos import Model

__all__ = ["answer_embeddings", "AnswerModel"]

answer_embeddings = Table(
    "answer_embeddings",
    Base.metadata,
    Column("answer_id", UUID(as_uuid=True), ForeignKey("answers.id"), primary_key=True),
    Column(
        "embedding_id",
        UUID(as_uuid=True),
        ForeignKey("embeddings.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class AnswerModel(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    question = Column(String)
    answer = Column(String)
    model = Column(Enum(Model), default=Model.Gpt3)

    embeddings = relationship(
        "EmbeddingModel", back_populates="answers", secondary=answer_embeddings
    )
