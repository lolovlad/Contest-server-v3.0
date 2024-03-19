"""empty message

Revision ID: 3095f7c129b4
Revises: 7302c0eb57f7
Create Date: 2024-03-14 12:02:38.836132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3095f7c129b4'
down_revision = '7302c0eb57f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contest_to_task',
    sa.Column('id_contest', sa.Integer(), nullable=False),
    sa.Column('id_task', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_contest'], ['contest.id'], ),
    sa.ForeignKeyConstraint(['id_task'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id_contest', 'id_task')
    )
    op.alter_column('contest_registration', 'id_user',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('contest_registration', 'id_contest',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('contest_registration', 'state_contest',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('contest_registration_id_team_fkey', 'contest_registration', type_='foreignkey')
    op.create_foreign_key(None, 'contest_registration', 'user', ['id_user'], ['id'])
    op.create_foreign_key(None, 'contest_registration', 'contest', ['id_contest'], ['id'])
    op.drop_column('contest_registration', 'id_team')
    op.drop_column('contest_registration', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contest_registration', sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('contest_registration', sa.Column('id_team', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'contest_registration', type_='foreignkey')
    op.drop_constraint(None, 'contest_registration', type_='foreignkey')
    op.create_foreign_key('contest_registration_id_team_fkey', 'contest_registration', 'team', ['id_team'], ['id'])
    op.alter_column('contest_registration', 'state_contest',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('contest_registration', 'id_contest',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('contest_registration', 'id_user',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('contest_to_task')
    # ### end Alembic commands ###