"""add column pincode

Revision ID: 67ac0beb357f
Revises: 
Create Date: 2024-01-11 12:38:25.208061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67ac0beb357f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('pincode', sa.Integer))


def downgrade() -> None:
    op.drop_column('user', 'pincode')
