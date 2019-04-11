"""empty message

Revision ID: 02da007ba281
Revises: 90d9d4ffd4e3
Create Date: 2019-03-01 00:23:24.806378

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02da007ba281'
down_revision = '90d9d4ffd4e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('translation_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=True),
    sa.Column('translation_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['translation_id'], ['translation.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('translation_like')
    # ### end Alembic commands ###