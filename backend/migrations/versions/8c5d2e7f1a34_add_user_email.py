"""add user email

Revision ID: 8c5d2e7f1a34
Revises: 7f4a1c2d9e10
"""
from alembic import op
import sqlalchemy as sa


revision = '8c5d2e7f1a34'
down_revision = '7f4a1c2d9e10'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=True))
        batch_op.create_index('ix_users_email', ['email'], unique=True)


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index('ix_users_email')
        batch_op.drop_column('email')
