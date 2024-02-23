from uuid import UUID, uuid4

from db.engine import db
from modules.document.models import DocumentModel
from modules.document.schemas import Document, DocumentParsed
from modules.embedding.utils import create_embeddings_for_document
from typing import Union


def get(id: UUID) -> Union[Document, None]:
    doc_model = db.session.query(DocumentModel).get(id)
    if doc_model is None:
        return None
    return Document.from_orm(doc_model)


def get_by_title(title: str) -> Union[Document, None]:
    doc_model = db.session.query(DocumentModel).filter(DocumentModel.title == title).first()
    if doc_model is None:
        return None
    return Document.from_orm(doc_model)


def get_all() -> list[Document]:
    doc_models = db.session.query(DocumentModel).all()
    return [Document.from_orm(doc_model) for doc_model in doc_models]


async def create(document: DocumentParsed) -> Document:
    doc_obj = DocumentModel(**document.dict(), id=uuid4())
    db.session.add(doc_obj)
    db.session.commit()
    db.session.refresh(doc_obj)

    await create_embeddings_for_document(doc_obj)

    return Document.from_orm(doc_obj)


def get_document_from_parsed_document(document: DocumentParsed) -> Document:
    doc_obj = DocumentModel(**document.dict(), id=uuid4())
    return Document.from_orm(doc_obj)


def delete(doc_id: str | None = None) -> None:
    if not doc_id:
        db.session.query(DocumentModel).delete()
    else:
        db.session.query(DocumentModel).filter(
            DocumentModel.id == doc_id
        ).delete()
    db.session.commit()
