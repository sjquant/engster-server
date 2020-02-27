"""empty message

Revision ID: c5dc02c95676
Revises: a97587b05de9
Create Date: 2020-02-28 02:24:00.104571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5dc02c95676'
down_revision = 'a97587b05de9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('translation', 'is_accepted')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('translation', sa.Column('is_accepted', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
