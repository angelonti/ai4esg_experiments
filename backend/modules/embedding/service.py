from uuid import UUID, uuid4
from enum import Enum

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy import text, Integer, UUID, Float, String

from db.engine import db
from modules.document.models import DocumentModel
from modules.embedding.models import EmbeddingModel
from modules.embedding.schemas import Embedding, EmbeddingCreate
from app_config import config

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class HybridFusionType(Enum):
    RECIPROCAL_RANK_FUSION = "reciprocal_rank"
    RELATIVE_SCORE_FUSION = "relative_score"


def get(id: UUID) -> Embedding:
    embedding_model = db.session.query(EmbeddingModel).get(id)
    if not embedding_model:
        raise HTTPException(status_code=404, detail="Embedding not found.")
    return Embedding.from_orm(embedding_model) if embedding_model else None


def get_similar(search_embedding: list[float], max_num: int, title: str = None) -> list[tuple[Embedding, float]]:
    db_embeddings = (
        db.session.query(EmbeddingModel)
        .join(DocumentModel, EmbeddingModel.document_id == DocumentModel.id)
        .where(DocumentModel.title == title if title else True)
        .order_by(EmbeddingModel.values.max_inner_product(search_embedding))
        .limit(max_num).all()
    )

    embeddings = [Embedding.from_orm(embedding) for embedding in db_embeddings]
    embedding_ids = [emb.id for emb in embeddings]
    distances = get_distances(search_embedding, embedding_ids)
    scores = [distance["score"] for distance in distances]

    embeddings_with_scores = list(zip(embeddings, scores))

    return embeddings_with_scores


def get_similar_hybrid(query: str, embedding: list[float], max_num: int, title: str = None) -> list[tuple[Embedding, float]]:

    scoring_function = HybridFusionType(config.hybrid_fusion).value

    text_chunks = f"""
        SELECT
            emb.id,
            emb.values,
            SUBSTRING(doc.text, emb."offset" + 1, emb.size) AS content
        FROM embeddings emb INNER JOIN documents doc
        ON emb.document_id = doc.id
        WHERE doc.title = :title
    """

    semantic_search = f"""
        SELECT
            id,
            RANK() OVER (ORDER BY -1*(values <#> :embedding) DESC) AS rank,
            -1*(values <#> :embedding) AS vector_score
        FROM chunks
        ORDER BY vector_score DESC
        LIMIT :max_num * 3    
    """

    keyword_search = f"""
        SELECT
            id,
            RANK() OVER (ORDER BY ts_rank_cd(to_tsvector('english', TRIM(content)), query) DESC) AS rank,
            ts_rank_cd(to_tsvector('english', TRIM(content)), query) AS text_score
        FROM chunks, plainto_tsquery('english', TRIM(:query)) query
        WHERE to_tsvector('english', TRIM(content)) @@ query
        ORDER BY text_score DESC
        LIMIT :max_num * 3    
    """

    aggregates = f"""
        SELECT
            MIN(text_score) - 0.0000001 AS min_text_score, -- avoid division by zero
            MAX(text_score) AS max_text_score,
            MIN(vector_score) - 0.0000001 AS min_vector_score, -- avoid division by zero
            MAX(vector_score) AS max_vector_score
        FROM semantic_search, keyword_search   
    """

    hybrid_search = f"""
        WITH chunks AS (
            {text_chunks}
        ),
        semantic_search AS (
            {semantic_search}
        ), --replace by vector_query
        keyword_search AS (
            {keyword_search}
        ),
        aggregates AS (
            {aggregates}
        )
        SELECT
            COALESCE(semantic_search.id, keyword_search.id) AS id,
            chunks.content AS content,
            semantic_search.vector_score,
            keyword_search.text_score,
            COALESCE((semantic_search.vector_score - aggregates.min_vector_score) / (aggregates.max_vector_score - aggregates.min_vector_score), 0.0) AS normalized_vector_score,
            COALESCE((keyword_search.text_score - aggregates.min_text_score) / (aggregates.max_text_score - aggregates.min_text_score), 0.0) AS normalized_text_score,
            semantic_search.rank AS vector_rank,
            keyword_search.rank AS text_rank,
            (
                (
                    COALESCE((semantic_search.vector_score - aggregates.min_vector_score) / (aggregates.max_vector_score - aggregates.min_vector_score), 0.0)
                )
                +
                (
                    COALESCE((keyword_search.text_score - aggregates.min_text_score) / (aggregates.max_text_score - aggregates.min_text_score), 0.0)
                )
            )/2 AS relative_score,
            COALESCE(1.0 /(:k + semantic_search.rank), 0.0) + COALESCE(1.0 /(:k + keyword_search.rank), 0.0) AS reciprocal_rank
        FROM aggregates, semantic_search
        FULL OUTER JOIN keyword_search
        ON semantic_search.id = keyword_search.id
        INNER JOIN chunks 
        ON chunks.id = COALESCE(semantic_search.id, keyword_search.id)
        ORDER BY {scoring_function} DESC   
    """

    sql = text(hybrid_search).columns(
        id=UUID,
        content=String,
        vector_score=Float,
        text_score=Float,
        normalized_vector_score=Float,
        normalized_text_score=Float,
        vector_rank=Integer,
        text_rank=Integer,
        relative_score=Float,
        reciprocal_rank=Float
    )

    records = db.session.execute(sql,
                                 {
                                    'query': query,
                                    'embedding': str(embedding),
                                    'max_num': max_num,
                                    'title': title,
                                    'k': 60
                                 }).fetchall()

    results = list()
    print(f"#####db returned {len(records)} records.")
    if config.use_reranking:
        pairs = [[query, record.content] for record in records]
        ids = [record.id for record in records]
        tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
        model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
        with torch.no_grad():
            inputs = tokenizer(pairs, padding=True, return_tensors='pt')
            scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
            reranked = [(id, pair[1], score)
                        for score, pair, id
                        in sorted(zip(scores, pairs, ids), reverse=True)
                        ]
            for id, _, score in reranked[:max_num]:
                results.append((get(id), float(score)))
    else:
        for record in records[:max_num]:
            results.append((get(record.id), record.__getattr__(scoring_function)))
    print(f"returning {len(results)} results.")
    return results


def get_distances(embedding1: list[float], embedding_ids: list[str]) -> list[dict[str, float]]:
    rows = (
        db.session.query(EmbeddingModel.id, (EmbeddingModel.values.max_inner_product(embedding1)).label("score"))
        .where(EmbeddingModel.id.in_(embedding_ids))
        .order_by(EmbeddingModel.values.max_inner_product(embedding1))
        .all()
    )
    distances = list({'id': str(row.id), 'score': -1*row.score} for row in rows) # query returns negative inner product
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
