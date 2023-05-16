"""initial

Revision ID: 5d7e9511951e
Revises: 
Create Date: 2023-04-20 19:12:02.149465

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d7e9511951e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contest',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_contest', sa.String(), nullable=True),
    sa.Column('datetime_start', sa.DateTime(), nullable=True),
    sa.Column('datetime_end', sa.DateTime(), nullable=True),
    sa.Column('description', sa.LargeBinary(), nullable=True),
    sa.Column('datetime_registration', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('state_contest', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('educational_organizations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_organizations', sa.String(), nullable=False),
    sa.Column('type_organizations', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_team', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('sename', sa.String(), nullable=True),
    sa.Column('secondname', sa.String(), nullable=True),
    sa.Column('foto', sa.String(), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('last_datatime_sign', sa.DateTime(), nullable=True),
    sa.Column('last_ip_sign', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contest_registration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('id_contest', sa.Integer(), nullable=True),
    sa.Column('id_team', sa.Integer(), nullable=True),
    sa.Column('state_contest', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_contest'], ['contest.id'], ),
    sa.ForeignKeyConstraint(['id_team'], ['team.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_contest', sa.Integer(), nullable=True),
    sa.Column('time_work', sa.Integer(), nullable=True),
    sa.Column('size_raw', sa.Integer(), nullable=True),
    sa.Column('type_input', sa.Integer(), nullable=True),
    sa.Column('type_output', sa.Integer(), nullable=True),
    sa.Column('name_task', sa.String(), nullable=False),
    sa.Column('description', sa.LargeBinary(), nullable=False),
    sa.Column('description_input', sa.LargeBinary(), nullable=False),
    sa.Column('description_output', sa.LargeBinary(), nullable=False),
    sa.Column('type_task', sa.Integer(), nullable=True),
    sa.Column('number_shipments', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_contest'], ['contest.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_registration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('id_team', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_team'], ['team.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_registration')
    op.drop_table('task')
    op.drop_table('contest_registration')
    op.drop_table('user')
    op.drop_table('team')
    op.drop_table('educational_organizations')
    op.drop_table('contest')
    # ### end Alembic commands ###
