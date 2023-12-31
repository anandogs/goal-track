"""Add completed column to task table

Revision ID: 7050549a066c
Revises: 152acb6b0699
Create Date: 2023-07-01 10:15:27.368481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7050549a066c'
down_revision = '152acb6b0699'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completed', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('completed')

    # ### end Alembic commands ###
