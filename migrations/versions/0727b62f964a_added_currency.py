"""added currency

Revision ID: 0727b62f964a
Revises: 9b2244c389f4
Create Date: 2025-02-15 11:30:44.619537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0727b62f964a'
down_revision: Union[str, None] = '9b2244c389f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currencies',
    sa.Column('code', sa.String(length=3), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('symbol', sa.String(length=5), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    op.add_column('products', sa.Column('currency_code', sa.String(length=3), nullable=True))
    op.create_foreign_key(None, 'products', 'currencies', ['currency_code'], ['code'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'currency_code')
    op.drop_table('currencies')
    # ### end Alembic commands ###
