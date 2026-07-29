import math
import uuid
from typing import List, Tuple, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.repositories.base import BaseRepository


class KnowledgeDocumentRepository(BaseRepository[KnowledgeDocument, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=KnowledgeDocument, session=session)


class KnowledgeChunkRepository(BaseRepository[KnowledgeChunk, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=KnowledgeChunk, session=session)

    async def search_similar_chunks(
        self, query_vector: List[float], top_k: int = 3
    ) -> List[Tuple[KnowledgeChunk, KnowledgeDocument, float]]:
        """
        Executes Cosine Similarity vector search over stored document chunks.
        Returns top-K tuples of (KnowledgeChunk, KnowledgeDocument, similarity_score).
        """
        stmt = (
            select(KnowledgeChunk, KnowledgeDocument)
            .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        )
        result = await self.session.execute(stmt)
        records = result.all()

        if not records:
            return []

        scored_results = []
        q_norm = math.sqrt(sum(x * x for x in query_vector)) or 1.0

        for chunk, doc in records:
            vec = chunk.embedding_vector
            if not vec or len(vec) != len(query_vector):
                continue

            dot_product = sum(q * v for q, v in zip(query_vector, vec))
            v_norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            similarity = dot_product / (q_norm * v_norm)

            scored_results.append((chunk, doc, round(similarity, 4)))

        scored_results.sort(key=lambda item: item[2], reverse=True)
        return scored_results[:top_k]
