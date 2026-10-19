"""Initial_tables

Revision ID: a2e868a40f75
Revises: e69e66c84b35
Create Date: 2026-10-12 08:38:51.058161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2e868a40f75'
down_revision: Union[str, Sequence[str], None] = 'e69e66c84b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
