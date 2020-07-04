"""empty message

Revision ID: cbfd705dc762
Revises: a34722390de1
Create Date: 2020-07-03 23:43:44.270396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbfd705dc762'
down_revision = 'a34722390de1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('nickname', sa.String(length=20), nullable=True))
    op.drop_column('results', 'middle_name')
    op.add_column('users', sa.Column('nickname', sa.String(length=100), nullable=True))
    op.drop_column('users', 'middle_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('middle_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_column('users', 'nickname')
    op.add_column('results', sa.Column('middle_name', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_column('results', 'nickname')
    # ### end Alembic commands ###
