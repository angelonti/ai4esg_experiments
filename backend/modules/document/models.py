from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base import Base
from modules.document.schemas import DocType


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String)
    text = Column(String)
    doc_type = Column(Enum(DocType))
    source = Column(String)
    embeddings = relationship("EmbeddingModel", cascade="all,delete", backref="documents")
    #penalties = relationship("PenaltyModel", cascade="all,delete", backref="documents")
    #requirements = relationship("RequirementModel", cascade="all,delete", backref="documents")
    #penalty_summaries = relationship("PenaltySummaryModel", cascade="all,delete", backref="documents")
    #requirement_summaries = relationship("RequirementSummaryModel", cascade="all,delete", backref="documents")