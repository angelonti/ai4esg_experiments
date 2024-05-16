from uuid import uuid4

from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base import Base

__all__ = ["AnnotatorModel", ""]


class AnnotatorModel(Base):
    __tablename__ = "annotators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    annotator_number = Column(Integer, autoincrement=True)
    password = Column(String)
    tasks = relationship("AnnotationTaskModel")


class AnnotationTaskModel(Base):
    __tablename__ = "annotator_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    annotator_number = Column(Integer, ForeignKey("annotators.annotator_number"))
    task_number = Column(Integer)
    data = Column(JSONB)
    finished = Column(Boolean, default=False)
