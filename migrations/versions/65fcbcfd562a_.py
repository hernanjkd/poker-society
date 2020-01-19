"""empty message

Revision ID: 65fcbcfd562a
Revises: 77bf1b25a2fa
Create Date: 2020-01-18 23:11:31.309332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65fcbcfd562a'
down_revision = '77bf1b25a2fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('casinos', sa.Column('h1', sa.String(length=200), nullable=True))
    op.add_column('results', sa.Column('winnings', sa.String(length=30), nullable=True))
    op.drop_column('results', 'earnings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('earnings', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_column('results', 'winnings')
    op.drop_column('casinos', 'h1')
    # ### end Alembic commands ###
