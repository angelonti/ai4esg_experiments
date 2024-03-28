"""add pgvector for embeddings

Revision ID: e94c3d08fc07
Revises: 7d304dd98081
Create Date: 2024-03-17 18:35:44.053224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e94c3d08fc07'
down_revision = '7d304dd98081'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("ALTER TABLE embeddings ALTER COLUMN values TYPE vector(1536)")
    # ### end Alembic commands ###


def downgrade() -> None:
    op.execute("ALTER TABLE embeddings ALTER COLUMN values TYPE float[]")
    op.execute("DROP EXTENSION IF EXISTS vector")
    # ### end Alembic commands ###
