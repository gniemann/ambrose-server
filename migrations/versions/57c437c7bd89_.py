"""empty message

Revision ID: 57c437c7bd89
Revises: 884948655465
Create Date: 2019-06-26 16:21:51.972447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57c437c7bd89'
down_revision = '884948655465'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('status_light')
    op.create_table('status_light',
                    sa.Column('device_id', sa.Integer(), nullable=False),
                    sa.Column('slot', sa.Integer(), nullable=False),
                    sa.Column('task_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
                    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
                    sa.PrimaryKeyConstraint('device_id', 'slot')
                    )
    op.add_column('device', sa.Column('supports_messages', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('status_light', sa.Column('user_id', sa.INTEGER(), nullable=False))
    op.drop_constraint(None, 'status_light', type_='foreignkey')
    op.create_foreign_key(None, 'status_light', 'user', ['user_id'], ['id'])
    op.drop_column('status_light', 'device_id')
    op.drop_column('device', 'supports_messages')
    # ### end Alembic commands ###
