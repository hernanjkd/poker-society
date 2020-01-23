"""empty message

Revision ID: f7385f5f13a8
Revises: 0b8efe2861a7
Create Date: 2020-01-23 04:47:42.640607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7385f5f13a8'
down_revision = '0b8efe2861a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tournaments', sa.Column('tarting_stack', sa.String(length=10), nullable=True))
    op.drop_column('tournaments', 'starting_stack')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tournaments', sa.Column('starting_stack', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('tournaments', 'tarting_stack')
    # ### end Alembic commands ###
