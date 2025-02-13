"""modified products removed NOT NULL constraint

Revision ID: 1dcfe388844e
Revises: ece8be7df701
Create Date: 2025-02-14 14:37:53.303142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dcfe388844e'
down_revision: Union[str, None] = 'ece8be7df701'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('products', 'price',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
    op.alter_column('products', 'stock_quantity',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('products', 'seller_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'seller_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('products', 'stock_quantity',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('products', 'price',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
    op.alter_column('products', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###
