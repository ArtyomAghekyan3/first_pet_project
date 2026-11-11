"""enable pgvector

Revision ID: c8884fab4ce6
Revises: 4271f723329c
Create Date: 2026-11-11 18:59:24.045407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8884fab4ce6'
down_revision: Union[str, Sequence[str], None] = '4271f723329c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
