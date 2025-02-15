"""modified products, created another table for product_images, meeting Boyce Codd normal form

Revision ID: 09b9288008a8
Revises: 4957721c83dc
Create Date: 2025-02-14 01:01:42.471298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '09b9288008a8'
down_revision: Union[str, None] = '4957721c83dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_images',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('products', 'images')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('images', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_table('product_images')
    # ### end Alembic commands ###
