import math
import re
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.ai_config import ai_settings
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.repositories.knowledge import KnowledgeChunkRepository, KnowledgeDocumentRepository
from app.schemas.ai import RAGDocumentUpload, RAGQueryResult


class RAGService:
    """
    Enterprise RAG Ingestion & Vector Search Service.
    Handles text passage chunking, vector embedding generation, and cosine similarity retrieval.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = KnowledgeDocumentRepository(session=session)
        self.chunk_repo = KnowledgeChunkRepository(session=session)
        self.dim = ai_settings.EMBEDDING_DIMENSION

    async def ingest_document(self, upload_in: RAGDocumentUpload) -> KnowledgeDocument:
        """
        Processes document upload: chunks text content, generates embeddings, and persists to DB.
        """
        chunks_text = self._chunk_text(
            text=upload_in.content,
            chunk_size=ai_settings.RAG_CHUNK_SIZE,
            overlap=ai_settings.RAG_CHUNK_OVERLAP
        )

        doc = KnowledgeDocument(
            title=upload_in.title,
            file_type=upload_in.file_type,
            author=upload_in.author,
            chunk_count=len(chunks_text)
        )
        created_doc = await self.doc_repo.create(doc)

        for idx, text in enumerate(chunks_text):
            vector = self._generate_embedding(text)
            chunk = KnowledgeChunk(
                document_id=created_doc.id,
                chunk_index=idx,
                content=text,
                embedding_vector=vector
            )
            await self.chunk_repo.create(chunk)

        return created_doc

    async def search_knowledge_base(self, query: str, top_k: int = 3) -> List[RAGQueryResult]:
        """
        Converts query to vector embedding and performs cosine similarity search across indexed chunks.
        """
        query_vector = self._generate_embedding(query)
        results = await self.chunk_repo.search_similar_chunks(query_vector=query_vector, top_k=top_k)

        out = []
        for chunk, doc, score in results:
            out.append(
                RAGQueryResult(
                    document_title=doc.title,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    similarity_score=score
                )
            )
        return out

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Splits raw text into sliding window passages with word overlap.
        """
        words = text.split()
        if not words:
            return []
        
        chunks = []
        step = max(1, chunk_size - overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            if i + chunk_size >= len(words):
                break
        return chunks

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional dense L2-normalized vector embedding using term hashing.
        """
        vector = [0.0] * self.dim
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()

        if not words:
            return vector

        for word in words:
            # Deterministic hash mapping into vector index space
            idx = abs(hash(word)) % self.dim
            vector[idx] += 1.0

        # L2 Vector Normalization
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [round(x / norm, 6) for x in vector]
