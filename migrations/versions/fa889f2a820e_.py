"""empty message

Revision ID: fa889f2a820e
Revises: 
Create Date: 2019-02-16 16:30:08.822330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa889f2a820e'
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
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
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
    sa.Column('_status', sa.String(), nullable=True),
    sa.Column('has_changed', sa.Boolean(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('devops_build_pipeline',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(), nullable=True),
    sa.Column('definition_id', sa.Integer(), nullable=True),
    sa.Column('pipeline', sa.String(), nullable=True),
    sa.Column('branch', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('devops_release_environment',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(), nullable=True),
    sa.Column('definition_id', sa.Integer(), nullable=True),
    sa.Column('pipeline', sa.String(), nullable=True),
    sa.Column('environment', sa.String(), nullable=True),
    sa.Column('environment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('devops_release_environment')
    op.drop_table('devops_build_pipeline')
    op.drop_table('task')
    op.drop_table('devops_account')
    op.drop_table('message')
    op.drop_table('account')
    op.drop_table('user')
    # ### end Alembic commands ###
