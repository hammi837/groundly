"""phase1 foundation schema

Revision ID: 0001_phase1_foundation
Revises:
Create Date: 2026-08-13

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001_phase1_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(
        """
        CREATE TABLE tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            api_key VARCHAR(64) UNIQUE NOT NULL,
            bot_name VARCHAR(120) NOT NULL DEFAULT 'Support Assistant',
            primary_color VARCHAR(7) NOT NULL DEFAULT '#0F766E',
            welcome_message TEXT NOT NULL DEFAULT 'Hi! Ask me anything about our practice.',
            starter_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
            allowed_origins TEXT[] NOT NULL DEFAULT '{}',
            rate_limit_rpm INT NOT NULL DEFAULT 60,
            webhook_url TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_users_tenant ON users(tenant_id)")

    op.execute(
        """
        CREATE TABLE documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            source_type VARCHAR(20) NOT NULL,
            source_name VARCHAR(255) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'processing',
            error_message TEXT,
            chunk_count INT NOT NULL DEFAULT 0,
            bytes INT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_documents_tenant_status ON documents(tenant_id, status)")

    op.execute(
        """
        CREATE TABLE chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            embedding DOUBLE PRECISION[] NOT NULL,
            content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_chunks_tenant ON chunks(tenant_id)")
    op.execute("CREATE INDEX idx_chunks_document ON chunks(document_id)")
    op.execute("CREATE INDEX idx_chunks_fts ON chunks USING gin (content_tsv)")

    op.execute(
        """
        CREATE TABLE conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            visitor_id VARCHAR(255) NOT NULL,
            visitor_email VARCHAR(255),
            started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_message_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_conversations_tenant_last ON conversations(tenant_id, last_message_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            cited_chunk_ids UUID[] NOT NULL DEFAULT '{}',
            retrieval_scores JSONB,
            was_fallback BOOLEAN NOT NULL DEFAULT false,
            prompt_tokens INT,
            completion_tokens INT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at)")

    op.execute(
        """
        CREATE TABLE leads (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            email VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            phone VARCHAR(64),
            question TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'new',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_leads_tenant_status ON leads(tenant_id, status, created_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE usage_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            event_type VARCHAR(40) NOT NULL,
            prompt_tokens INT NOT NULL DEFAULT 0,
            completion_tokens INT NOT NULL DEFAULT 0,
            embedding_tokens INT NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_usage_tenant_created ON usage_events(tenant_id, created_at DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS usage_events CASCADE")
    op.execute("DROP TABLE IF EXISTS leads CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS chunks CASCADE")
    op.execute("DROP TABLE IF EXISTS documents CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS tenants CASCADE")
