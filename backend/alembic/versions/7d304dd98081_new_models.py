"""new models

Revision ID: 7d304dd98081
Revises: 959c622cb128
Create Date: 2023-08-18 17:58:37.109179

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7d304dd98081"
down_revision = "959c622cb128"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE model_enum_new ADD VALUE IF NOT EXISTS 'LLAMA_2_7B'")
    op.execute("ALTER TYPE model_enum_new ADD VALUE IF NOT EXISTS 'LLAMA_2_13B'")
    op.execute("ALTER TYPE model_enum_new ADD VALUE IF NOT EXISTS 'LLAMA_2_70B'")


def downgrade() -> None:
    # no downgrade, so can keep data. Upgrade robust to being executed multiple times.
    pass
