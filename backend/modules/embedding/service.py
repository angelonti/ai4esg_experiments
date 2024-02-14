from uuid import UUID, uuid4

from fastapi import HTTPException
from db.engine import db
from sqlalchemy.orm import joinedload

from modules.document.models import DocumentModel
from modules.embedding.models import EmbeddingModel
from modules.embedding.schemas import Embedding, EmbeddingCreate


def get(id: UUID) -> Embedding:
    embedding_model = db.session.query(EmbeddingModel).get(id)
    if not embedding_model:
        raise HTTPException(status_code=404, detail="Embedding not found.")
    return Embedding.from_orm(embedding_model) if embedding_model else None


def get_all() -> list[Embedding]:
    embeddings = (
        db.session.query(EmbeddingModel)
        .join(DocumentModel, EmbeddingModel.document_id == DocumentModel.id)
        .options(joinedload(EmbeddingModel.document))
        .all()
    )

    return [Embedding.from_orm(embedding) for embedding in embeddings]


def create(embedding: EmbeddingCreate) -> Embedding:
    embedding_obj = EmbeddingModel(**embedding.dict(), id=uuid4())
    db.session.add(embedding_obj)
    db.session.commit()
    db.session.refresh(embedding_obj)
    return Embedding.from_orm(embedding_obj)


def get_embedding_from_embedding_create(embedding: EmbeddingCreate, document) -> Embedding:
    embedding_obj = EmbeddingModel(**embedding.dict(), id=uuid4())
    embed_dict = dict.copy(embedding_obj.__dict__)
    embed_dict['document'] = document
    return Embedding.parse_obj(embed_dict)
