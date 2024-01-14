"""update model options

Revision ID: 4f8ecc9dfb6c
Revises: a487f4833b67
Create Date: 2023-07-25 16:29:42.822871

"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op
from modules.llm.llm_infos import Model

# revision identifiers, used by Alembic.
revision = "4f8ecc9dfb6c"
down_revision = "a487f4833b67"
branch_labels = None
depends_on = None


def upgrade():
    # create new ENUM type
    new_model_enum = ENUM(
        "Gpt3", "Gpt4", "Falcon", name="model_enum_new", create_type=True
    )
    new_model_enum.create(op.get_bind())

    # add new column with new ENUM type
    op.add_column("answers", sa.Column("model_new", new_model_enum, nullable=True))

    # copy values from the old column to new one
    op.execute(
        """
        UPDATE answers
        SET model_new = 
            CASE
            WHEN model='OpenAI' THEN 'Gpt3'::model_enum_new
            ELSE model::text::model_enum_new
            END
    """
    )

    # drop the old column
    op.drop_column("answers", "model")

    # rename new column
    op.alter_column("answers", "model_new", new_column_name="model")


def downgrade():
    # create old ENUM type
    old_model_enum = ENUM("OpenAI", "Falcon", name="model_enum_old", create_type=True)
    old_model_enum.create(op.get_bind())

    # add old column with old ENUM type
    op.add_column("answers", sa.Column("model_old", old_model_enum, nullable=True))

    # copy values from the new column to old one
    op.execute(
        """
        UPDATE answers
        SET model_old = 
            CASE
            WHEN model='Gpt3' THEN 'OpenAI'::model_enum_old
            ELSE model::text::model_enum_old
            END
    """
    )

    # drop the new column
    op.drop_column("answers", "model")

    # rename old column
    op.alter_column("answers", "model_old", new_column_name="model")

    # remove the new ENUM type
    ENUM(name="model_enum_new").drop(op.get_bind(), checkfirst=False)
