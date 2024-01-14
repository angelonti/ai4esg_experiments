"""added doc cascade

Revision ID: 30b1a9fafb5f
Revises: 2f915025137d
Create Date: 2023-07-06 11:44:19.202131

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "30b1a9fafb5f"
down_revision = "2f915025137d"
branch_labels = None
depends_on = None


def upgrade():
    # Alter foreign key from embeddings to documents
    op.drop_constraint("embeddings_document_id_fkey", "embeddings", type_="foreignkey")
    op.create_foreign_key(
        None, "embeddings", "documents", ["document_id"], ["id"], ondelete="CASCADE"
    )

    # Alter foreign key from answer_embeddings to embeddings
    op.drop_constraint(
        "answer_embeddings_embedding_id_fkey", "answer_embeddings", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "answer_embeddings",
        "embeddings",
        ["embedding_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # Undo alterations
    op.drop_constraint(None, "embeddings", type_="foreignkey")
    op.create_foreign_key(
        "embeddings_document_id_fkey",
        "embeddings",
        "documents",
        ["document_id"],
        ["id"],
    )

    op.drop_constraint(None, "answer_embeddings", type_="foreignkey")
    op.create_foreign_key(
        "answer_embeddings_embedding_id_fkey",
        "answer_embeddings",
        "embeddings",
        ["embedding_id"],
        ["id"],
    )
