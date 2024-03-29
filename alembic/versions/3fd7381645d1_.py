"""empty message

Revision ID: 3fd7381645d1
Revises: 9037bd61d896
Create Date: 2021-03-20 01:22:11.653036

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3fd7381645d1'
down_revision = '9037bd61d896'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('translation_review',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('translation', sa.Text(), nullable=False),
    sa.Column('message', sa.String(length=400), nullable=True),
    sa.Column('translation_id', sa.Integer(), nullable=False),
    sa.Column('reviewer_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['reviewer_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['translation_id'], ['translation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('translation', sa.Column('status', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('translation', 'status')
    op.drop_table('translation_review')
    # ### end Alembic commands ###
