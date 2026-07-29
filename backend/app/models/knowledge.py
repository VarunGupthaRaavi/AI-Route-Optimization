import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class KnowledgeDocument(BaseModel):
    """
    SQLAlchemy 2.0 Knowledge Document Entity Model.
    Represents uploaded enterprise logistics SOPs, manual PDFs, and operational policy files.
    """
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, doc="Document title or original filename"
    )
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PDF", doc="Document format extension (PDF, TXT, MD)"
    )
    author: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, doc="Document author or department source"
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Number of extracted text chunks"
    )

    chunks: Mapped[List["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk", back_populates="document", cascade="all, delete-orphan"
    )


class KnowledgeChunk(BaseModel):
    """
    SQLAlchemy 2.0 Knowledge Chunk Entity Model.
    Stores extracted text passages and vector embeddings for Enterprise RAG vector search.
    """
    __tablename__ = "knowledge_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="Passage sequence index within document"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Raw textual passage chunk"
    )
    embedding_vector: Mapped[list] = mapped_column(
        JSON, nullable=False, doc="Dense floating point vector embedding array"
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument", back_populates="chunks"
    )
