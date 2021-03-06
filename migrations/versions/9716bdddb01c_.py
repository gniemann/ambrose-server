"""empty message

Revision ID: 9716bdddb01c
Revises: 433011bd0c6d
Create Date: 2019-03-03 13:33:59.252816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9716bdddb01c'
down_revision = '433011bd0c6d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('github_repoistory_status',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('repo_name', sa.String(), nullable=True),
    sa.Column('pr_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('github_repoistory_status')
    # ### end Alembic commands ###
