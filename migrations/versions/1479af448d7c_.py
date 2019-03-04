"""empty message

Revision ID: 1479af448d7c
Revises: 3d554b9d3324
Create Date: 2019-03-01 16:49:09.733419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1479af448d7c'
down_revision = '3d554b9d3324'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('random_message',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_table('random_message_choice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['random_message.message_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('random_message_choice')
    op.drop_table('random_message')
    # ### end Alembic commands ###