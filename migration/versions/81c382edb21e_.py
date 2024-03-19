"""empty message

Revision ID: 81c382edb21e
Revises: 76fd66994fa9
Create Date: 2024-03-13 11:00:56.231010

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '81c382edb21e'
down_revision = '76fd66994fa9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type_task',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('task', sa.Column('uuid', sa.UUID(), nullable=False))
    op.add_column('task', sa.Column('id_type_task', sa.Integer(), nullable=True))
    op.alter_column('task', 'description_input',
               existing_type=postgresql.BYTEA(),
               nullable=True)
    op.alter_column('task', 'description_output',
               existing_type=postgresql.BYTEA(),
               nullable=True)
    op.drop_constraint('task_id_contest_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'type_task', ['id_type_task'], ['id'])
    op.drop_column('task', 'type_input')
    op.drop_column('task', 'type_output')
    op.drop_column('task', 'size_raw')
    op.drop_column('task', 'id_contest')
    op.drop_column('task', 'number_shipments')
    op.drop_column('task', 'type_task')
    op.drop_column('task', 'time_work')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('time_work', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('type_task', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('number_shipments', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('id_contest', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('size_raw', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('type_output', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('type_input', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_id_contest_fkey', 'task', 'contest', ['id_contest'], ['id'])
    op.alter_column('task', 'description_output',
               existing_type=postgresql.BYTEA(),
               nullable=False)
    op.alter_column('task', 'description_input',
               existing_type=postgresql.BYTEA(),
               nullable=False)
    op.drop_column('task', 'id_type_task')
    op.drop_column('task', 'uuid')
    op.drop_table('type_task')
    # ### end Alembic commands ###