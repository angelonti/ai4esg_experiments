import asyncio
from typing import NamedTuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Element

from config import config
from modules.document.models import DocumentModel
from modules.embedding.schemas import Embedding, EmbeddingCreate
from modules.embedding.service import create, get_embedding_from_embedding_create, get_distances
from modules.llm.schemas import EmbeddingResponse
from modules.llm.utils import get_text_embedding


class Chunk(NamedTuple):
    text: str
    offset: int
    size: int
    page_number: int = 0


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


async def create_embeddings_for_chunks(document: DocumentModel, chunks: list[Chunk]) -> list[Embedding]:
    tasks: list[EmbeddingResponse] = []
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
                    page_number=chunks[i].page_number
                ),
            )
        )
        print(f"chunk {i} of {len(embeddings)} done")
    return embedding_objs


async def create_embeddings_from_contexts(document: DocumentModel, json_data: dict) -> list[Embedding]:
    tasks: list[EmbeddingResponse] = []
    embedding_objs = []
    if "paragraphs" in json_data:
        for paragraph in json_data["paragraphs"]:
            text = paragraph["context"]
            tasks.append(get_text_embedding(text))
        embeddings = await asyncio.gather(*tasks)
        for i, embedding in enumerate(embeddings):
            context = json_data["paragraphs"][i]["context"]
            size = len(context)
            offset = document.text.find(context)
            embedding_objs.append(
                create(
                    EmbeddingCreate(
                        document_id=document.id,
                        values=embedding.data[0].embedding,
                        document=document,
                        offset=offset,
                        size=size,
                        page_number=0
                    )
                )
            )
    return embedding_objs


def get_embeddings_from_contexts(document: DocumentModel, json_data: dict) -> list[Embedding]:
    embedding_objs = []
    if "data" in json_data:
        for policy in json_data["data"]:
            for paragraph in policy["paragraphs"]:
                context = paragraph["context"]
                size = len(context)
                offset = document.text.find(context)
                embedding_objs.append(
                    get_embedding_from_embedding_create(
                        EmbeddingCreate(
                            document_id=document.id,
                            values=[],
                            document=document,
                            offset=offset,
                            size=size,
                        ),
                        document=document,
                    )
                )
    return embedding_objs


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


def chunk_partitions(partitions: list[Element]) -> list[Chunk]:
    chunk_tuples = chunk_by_title(partitions, max_characters=config.chunk_size * 2, new_after_n_chars=config.chunk_size)
    count = 0
    chunks = []
    for i, chunk in enumerate(chunk_tuples):
        text_chunk = chunk.text
        page_number = chunk.metadata.page_number
        size = len(text_chunk)
        offset = count
        chunks.append(Chunk(text=text_chunk, offset=offset, size=size, page_number=page_number))
        count += size
    return chunks


def to_relevant_embeddings(answer_embeddings_with_scores: list[tuple[Embedding, float]]) -> list[dict]:
    # print(f"#### length embeddings with scores: {len(answer_embeddings_with_scores)}")
    relevant_embeddings = list()
    score_type = "cross_encoder" if config.use_reranking else config.hybrid_fusion if config.use_hybrid else "cosine_similarity"
    for i, (embedding, score) in enumerate(answer_embeddings_with_scores):
        # print(f"creating relevant embedding for id: {embedding.id} and score {score}")
        relevant_embedding = {
            "embedding_id": str(embedding.id),
            "rank": i + 1,
            "title": embedding.document.title,
            "offset": embedding.offset,
            "score": score,
            "score_type": score_type,
            "reranked": config.use_reranking,
            "text": embedding.text
        }
        relevant_embeddings.append(relevant_embedding)
    return relevant_embeddings
