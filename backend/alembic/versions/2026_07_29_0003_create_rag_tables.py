"""create rag knowledge tables

Revision ID: 2026_07_29_0003
Revises: 2026_07_29_0002
Create Date: 2026-07-29 08:37:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_07_29_0003'
down_revision: Union[str, None] = '2026_07_29_0002'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create knowledge_documents table
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False, server_default='PDF'),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_documents_title'), 'knowledge_documents', ['title'], unique=False)

    # 2. Create knowledge_chunks table
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('document_id', sa.Uuid(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding_vector', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_chunks_document_id'), 'knowledge_chunks', ['document_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_knowledge_chunks_document_id'), table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_documents_title'), table_name='knowledge_documents')
    op.drop_table('knowledge_documents')
