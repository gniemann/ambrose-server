"""empty message

Revision ID: 459ca10847fb
Revises: 
Create Date: 2019-02-19 09:24:39.142092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '459ca10847fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('_type', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('application_insights_account',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.String(), nullable=True),
    sa.Column('api_key', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('datetime_message',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('dateformat', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_table('devops_account',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('organization', sa.String(), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('_type', sa.String(), nullable=True),
    sa.Column('_value', sa.String(), nullable=True),
    sa.Column('_prev_value', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('application_insight_metric',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('metric', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('devops_build_pipeline',
    sa.Column('project', sa.String(), nullable=True),
    sa.Column('definition_id', sa.Integer(), nullable=True),
    sa.Column('pipeline', sa.String(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('branch', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('devops_release_environment',
    sa.Column('project', sa.String(), nullable=True),
    sa.Column('definition_id', sa.Integer(), nullable=True),
    sa.Column('pipeline', sa.String(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('environment', sa.String(), nullable=True),
    sa.Column('environment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('status_light',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('slot', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'slot')
    )
    op.create_table('task_message',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('message_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_message')
    op.drop_table('status_light')
    op.drop_table('devops_release_environment')
    op.drop_table('devops_build_pipeline')
    op.drop_table('application_insight_metric')
    op.drop_table('task')
    op.drop_table('devops_account')
    op.drop_table('datetime_message')
    op.drop_table('application_insights_account')
    op.drop_table('message')
    op.drop_table('account')
    op.drop_table('user')
    # ### end Alembic commands ###