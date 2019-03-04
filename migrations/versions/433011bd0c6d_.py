"""empty message

Revision ID: 433011bd0c6d
Revises: e4f6c754f361
Create Date: 2019-03-01 22:40:24.550324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '433011bd0c6d'
down_revision = 'e4f6c754f361'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('github_account',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('github_account')
    # ### end Alembic commands ###