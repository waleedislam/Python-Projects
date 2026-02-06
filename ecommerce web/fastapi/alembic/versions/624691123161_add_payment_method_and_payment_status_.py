"""add payment_method and payment_status to orders

Revision ID: 624691123161
Revises: e06be8535607
Create Date: 2026-02-06 15:19:23.181324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '624691123161'
down_revision: Union[str, Sequence[str], None] = 'e06be8535607'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
