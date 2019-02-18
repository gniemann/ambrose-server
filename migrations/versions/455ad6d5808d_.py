"""empty message

Revision ID: 455ad6d5808d
Revises: e6f56a4e5d9d
Create Date: 2019-02-18 09:45:44.102360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '455ad6d5808d'
down_revision = 'e6f56a4e5d9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('prev_status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'prev_status')
    # ### end Alembic commands ###
