"""merge multiple heads

Revision ID: 5343e0f50cff
Revises: 172d7621794f, 8cf9291d1990
Create Date: 2026-03-04 17:16:39.900397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5343e0f50cff'
down_revision: Union[str, Sequence[str], None] = ('172d7621794f', '8cf9291d1990')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
