"""changed product to accept many images

Revision ID: b84cb305f043
Revises: 33ae2a992d79
Create Date: 2025-02-11 14:53:01.175877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b84cb305f043'
down_revision: Union[str, None] = '33ae2a992d79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('images', sa.JSON(), nullable=True))
    op.drop_column('products', 'image_url')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('image_url', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('products', 'images')
    # ### end Alembic commands ###
