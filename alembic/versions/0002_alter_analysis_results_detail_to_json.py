"""alter analysis_results detail to json

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "analysis_results",
        "detail",
        existing_type=sa.Text(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using="detail::json",
    )


def downgrade() -> None:
    op.alter_column(
        "analysis_results",
        "detail",
        existing_type=sa.JSON(),
        type_=sa.Text(),
        existing_nullable=True,
        postgresql_using="detail::text",
    )
