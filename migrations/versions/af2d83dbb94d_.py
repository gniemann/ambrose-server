"""empty message

Revision ID: af2d83dbb94d
Revises: ea49f54d739a
Create Date: 2019-02-19 12:24:49.700782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af2d83dbb94d'
down_revision = 'ea49f54d739a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('datetime_message', sa.Column('timezone', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('datetime_message', 'timezone')
    # ### end Alembic commands ###