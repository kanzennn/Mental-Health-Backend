"""merge prediction and xai into analysis_sessions

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("analysis_sessions", sa.Column("category", sa.String(), nullable=True))
    op.add_column("analysis_sessions", sa.Column("confidence", sa.Float(), nullable=True))
    op.add_column("analysis_sessions", sa.Column("model_version", sa.String(), nullable=True))
    op.add_column("analysis_sessions", sa.Column("method", sa.String(), nullable=True))

    op.drop_table("xai_results")
    op.drop_table("predictions")


def downgrade() -> None:
    op.create_table(
        "predictions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "xai_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("prediction_id", sa.UUID(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("explanation_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.drop_column("analysis_sessions", "method")
    op.drop_column("analysis_sessions", "model_version")
    op.drop_column("analysis_sessions", "confidence")
    op.drop_column("analysis_sessions", "category")
