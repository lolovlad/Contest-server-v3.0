"""empty message

Revision ID: 3c9396e96f75
Revises: 5d7e9511951e
Create Date: 2024-03-06 19:15:18.113412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c9396e96f75'
down_revision = '5d7e9511951e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type_user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('id_type', sa.Integer(), nullable=True))
    op.alter_column('user', 'foto',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_foreign_key(None, 'user', 'type_user', ['id_type'], ['id'])
    op.drop_column('user', 'type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('type', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.alter_column('user', 'foto',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('user', 'id_type')
    op.drop_table('type_user')
    # ### end Alembic commands ###