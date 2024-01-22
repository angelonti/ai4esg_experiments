import asyncio

from config import config
from modules.document.models import DocumentModel
from modules.embedding.schemas import Embedding, EmbeddingCreate
from modules.embedding.service import create
from modules.llm.schemas import EmbeddingResponse
from modules.llm.utils import get_text_embedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import NamedTuple


async def create_embeddings_for_document(document: DocumentModel) -> list[Embedding]:
    tasks: list[EmbeddingResponse] = []
    chunks = text_to_chunks(document.text)
    for chunk in chunks:
        text = chunk.text
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
                    offset=chunks[i].offset,
                    size=chunks[i].size,
                ),
            )
        )
    return embedding_objs

#async def create_embeddings_for_document(document: DocumentModel) -> list[Embedding]:
#    tasks: list[EmbeddingResponse] = []
#    offsets = range(0, len(document.text), config.chunk_size - config.overlap_size)
#    for offset in offsets:
#        text = document.text[offset: offset + config.chunk_size]
#        if config.add_title:
#            text = f"title:{document.title}\n{text}"
#        tasks.append(get_text_embedding(text))
#
#    embedding_objs = []
#    embeddings = await asyncio.gather(*tasks)
#    for i, embedding in enumerate(embeddings):
#        embedding_objs.append(
#            create(
#                EmbeddingCreate(
#                    document_id=document.id,
#                    values=embedding.data[0].embedding,
#                    document=document,
#                    offset=offsets[i],
#                    size=config.chunk_size,
#                ),
#            )
#        )
#    return embedding_objs


class Chunk(NamedTuple):
    text: str
    offset: int
    size: int


def text_to_chunks(text: str) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=config.chunk_size,
        chunk_overlap=config.overlap_size,
    )
    chunks = []
    text_chunks = splitter.split_text(text)
    for i, chunk in enumerate(text_chunks):
        offset = text.find(chunk)
        size = len(chunk)
        chunks.append(Chunk(text=chunk, offset=offset, size=size))
    return chunks
