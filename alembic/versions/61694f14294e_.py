"""empty message

Revision ID: 61694f14294e
Revises: 5e41fc06d136
Create Date: 2019-05-11 23:08:26.637124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61694f14294e'
down_revision = '5e41fc06d136'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('translation', sa.Column(
        'is_accepted', sa.Boolean(), server_default='f', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('translation', 'is_accepted')
    # ### end Alembic commands ###