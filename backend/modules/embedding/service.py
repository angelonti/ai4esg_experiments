from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from db.engine import db
from modules.document.models import DocumentModel
from modules.embedding.models import EmbeddingModel
from modules.embedding.schemas import Embedding, EmbeddingCreate


def get(id: UUID) -> Embedding:
    embedding_model = db.session.query(EmbeddingModel).get(id)
    if not embedding_model:
        raise HTTPException(status_code=404, detail="Embedding not found.")
    return Embedding.from_orm(embedding_model) if embedding_model else None


def get_similar(embedding: list[float], max_num: int, title: str = None) -> list[Embedding]:
    db_embeddings = (
        db.session.query(EmbeddingModel)
        .join(DocumentModel, EmbeddingModel.document_id == DocumentModel.id)
        .where(DocumentModel.title == title if title else True)
        .order_by(EmbeddingModel.values.max_inner_product(embedding))
        .limit(max_num).all()
    )

    return [Embedding.from_orm(embedding) for embedding in db_embeddings]


def get_distances(embedding1: list[float], embedding_ids: list[str]) -> list[tuple[str, float]]:
    rows = (
        db.session.query(EmbeddingModel.id, EmbeddingModel.values.max_inner_product(embedding1))
        .where(EmbeddingModel.id.in_(embedding_ids))
        .order_by(EmbeddingModel.values.max_inner_product(embedding1))
        .all()
    )
    distances = [(str(row[0]), row[1]*(-1)) for row in rows]
    return distances


def get_all(title: str = None) -> list[Embedding]:
    embeddings = (
        db.session.query(EmbeddingModel)
        .join(DocumentModel, EmbeddingModel.document_id == DocumentModel.id)
        .where(DocumentModel.title == title if title else True)
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
