"""
Create users and auth_events tables with proper constraints and relationships.

Revision ID: 002
Revises: 001
Create Date: 2026-01-14 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.CheckConstraint('email = LOWER(email)', name='check_email_lowercase'),
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active'])

    # Create auth_events table
    op.create_table(
        'auth_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_index('idx_auth_events_user_id', 'auth_events', ['user_id'])
    op.create_index('idx_auth_events_type', 'auth_events', ['event_type'])
    op.create_index('idx_auth_events_created_at', 'auth_events', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_auth_events_created_at', table_name='auth_events')
    op.drop_index('idx_auth_events_type', table_name='auth_events')
    op.drop_index('idx_auth_events_user_id', table_name='auth_events')
    op.drop_index('idx_users_active', table_name='users')
    op.drop_index('idx_users_email', table_name='users')

    # Drop tables
    op.drop_table('auth_events')
    op.drop_table('users')