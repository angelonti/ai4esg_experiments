"""add annotation tables

Revision ID: 90d718023088
Revises: 3ef828b08faf
Create Date: 2024-05-15 09:27:10.123919

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '90d718023088'
down_revision = '3ef828b08faf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("annotators",
                    sa.Column("id", sa.UUID(), nullable=False),
                    sa.Column("annotator_number", sa.Integer(), unique=True, nullable=False),
                    sa.Column("password", sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint("id")
                    )

    op.create_table("annotator_tasks",
                    sa.Column("id", sa.UUID(), nullable=False),
                    sa.Column("annotator_number", sa.Integer(), nullable=False),
                    sa.Column("task_number", sa.Integer(), nullable=False),
                    sa.Column("data", sa.JSON(), nullable=False),
                    sa.Column("finished", sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint("id"),
                    sa.ForeignKeyConstraint(
                        ["annotator_number"],
                        ["annotators.annotator_number"],
                    )
                    )


def downgrade() -> None:
    op.drop_table("annotators")
    op.drop_table("annotator_tasks")
