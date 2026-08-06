"""add file size and query indexes

Revision ID: 7f4a1c2d9e10
Revises: 2a3b5c7d8e9f
"""
from alembic import op
import sqlalchemy as sa


revision = '7f4a1c2d9e10'
down_revision = '2a3b5c7d8e9f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('files') as batch_op:
        batch_op.add_column(sa.Column('file_size', sa.BigInteger(), nullable=False, server_default='0'))
    with op.batch_alter_table('messages') as batch_op:
        batch_op.create_index('ix_messages_conversation_time', ['sender_id', 'receiver_id', 'send_time'])
    with op.batch_alter_table('notifications') as batch_op:
        batch_op.create_index('ix_notifications_user_read_time', ['user_id', 'is_read', 'create_time'])


def downgrade():
    with op.batch_alter_table('notifications') as batch_op:
        batch_op.drop_index('ix_notifications_user_read_time')
    with op.batch_alter_table('messages') as batch_op:
        batch_op.drop_index('ix_messages_conversation_time')
    with op.batch_alter_table('files') as batch_op:
        batch_op.drop_column('file_size')
