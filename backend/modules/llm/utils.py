import asyncio

import aiohttp
import numpy as np
from fastapi import HTTPException

from config import config
from modules.llm.schemas import EmbeddingResponse


def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


semaphore = asyncio.Semaphore(10)


async def get_text_embedding(text: str) -> EmbeddingResponse:
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.openai_api_key}"
    }

    async with semaphore, aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"input": text, "model": config.embedding_model},
            headers=headers,
        ) as resp:
            data = await resp.json()
            if "error" in data:
                raise HTTPException(
                    status_code=400,
                    detail=data["error"].get(
                        "message", "An unexpected OpenAI error occurred."
                    )
                )
            return EmbeddingResponse(**data)
