"""merge availability and fixed roles branches

Revision ID: b70f5897c322
Revises: 172d7621794f, 8cf9291d1990
Create Date: 2026-03-07 18:45:40.290718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b70f5897c322'
down_revision: Union[str, Sequence[str], None] = ('172d7621794f', '8cf9291d1990')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
