"""empty message

Revision ID: 884948655465
Revises: d70149e16d2a
Create Date: 2019-04-30 14:25:03.820719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '884948655465'
down_revision = 'd70149e16d2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('uses_webhook', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'uses_webhook')
    # ### end Alembic commands ###
