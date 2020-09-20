"""empty message

Revision ID: 046e93cf2e1f
Revises: 6b75e017e18a
Create Date: 2020-09-20 01:01:55.854863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '046e93cf2e1f'
down_revision = '6b75e017e18a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('line_like_idx_id', 'line_like', ['id'], unique=False)
    op.create_index('translation_like_idx_id', 'translation_like', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('translation_like_idx_id', table_name='translation_like')
    op.drop_index('line_like_idx_id', table_name='line_like')
    # ### end Alembic commands ###
