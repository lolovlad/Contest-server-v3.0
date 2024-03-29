"""empty message

Revision ID: 2066901a61ab
Revises: cdf9d02f2747
Create Date: 2024-03-09 11:12:23.660894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2066901a61ab'
down_revision = 'cdf9d02f2747'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('type_organizations', sa.Column('postfix', sa.String(length=10), nullable=True))
    op.add_column('user', sa.Column('stage_edu', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'stage_edu')
    op.drop_column('type_organizations', 'postfix')
    # ### end Alembic commands ###
