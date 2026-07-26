"""add is_hidden to posts

Revision ID: 2a3b5c7d8e9f
Revises: 3213e5124ed3
Create Date: 2026-07-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a3b5c7d8e9f'
down_revision = '3213e5124ed3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_hidden', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('is_hidden')
