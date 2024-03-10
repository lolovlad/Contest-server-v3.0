"""empty message

Revision ID: ba5a4b8da0ad
Revises: 3c9396e96f75
Create Date: 2024-03-09 10:46:24.096790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba5a4b8da0ad'
down_revision = '3c9396e96f75'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type_organizations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('educational_organizations', sa.Column('uuid', sa.UUID(), nullable=False))
    op.add_column('educational_organizations', sa.Column('type_organizations_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'educational_organizations', 'type_organizations', ['type_organizations_id'], ['id'])
    op.drop_column('educational_organizations', 'type_organizations')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('educational_organizations', sa.Column('type_organizations', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'educational_organizations', type_='foreignkey')
    op.drop_column('educational_organizations', 'type_organizations_id')
    op.drop_column('educational_organizations', 'uuid')
    op.drop_table('type_organizations')
    # ### end Alembic commands ###
