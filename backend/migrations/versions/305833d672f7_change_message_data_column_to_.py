"""change message.data column to LargeBinary type

Revision ID: 305833d672f7
Revises: 85f8b387444f
Create Date: 2026-08-08 21:39:32.626172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '305833d672f7'
down_revision: Union[str, Sequence[str], None] = '85f8b387444f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # text -> bytea: postgres не кастует автоматически, нужен USING
    op.alter_column('messages', 'data',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.LargeBinary(),
               existing_nullable=False,
               postgresql_using='data::bytea')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('messages', 'data',
               existing_type=sa.LargeBinary(),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=False,
               postgresql_using='data::text')