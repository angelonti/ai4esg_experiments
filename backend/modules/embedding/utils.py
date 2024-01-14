import asyncio

from config import config
from modules.document.models import DocumentModel
from modules.embedding.schemas import Embedding, EmbeddingCreate
from modules.embedding.service import create
from modules.llm.schemas import EmbeddingResponse
from modules.llm.utils import get_text_embedding


async def create_embeddings_for_document(document: DocumentModel) -> list[Embedding]:
    tasks: list[EmbeddingResponse] = []
    offsets = range(0, len(document.text), config.chunk_size - config.overlap_size)
    for offset in offsets:
        text = document.text[offset : offset + config.chunk_size]
        if config.add_title:
            text = f"title:{document.title}\n{text}"
        tasks.append(get_text_embedding(text))

    embedding_objs = []
    embeddings = await asyncio.gather(*tasks)
    for i, embedding in enumerate(embeddings):
        embedding_objs.append(
            create(
                EmbeddingCreate(
                    document_id=document.id,
                    values=embedding.data[0].embedding,
                    document=document,
                    offset=offsets[i],
                    size=config.chunk_size,
                ),
            )
        )
    return embedding_objs
