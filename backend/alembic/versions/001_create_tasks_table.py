"""create tasks table

Revision ID: 001
Revises:
Create Date: 2026-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Detect dialect
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'

    # Create tasks table
    # Use generic sa.Uuid which maps to UUID on Postgres and CHAR(32)/GUID on SQLite
    op.create_table(
        'tasks',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # CHECK constraints
        sa.CheckConstraint('length(trim(title)) > 0', name='check_title_not_empty'),
        sa.CheckConstraint(
            '(is_completed = false AND completed_at IS NULL) OR (is_completed = true AND completed_at IS NOT NULL)',
            name='check_completion_consistency'
        ),
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_composite', 'tasks', ['user_id', 'id'])
    op.create_index('idx_tasks_created_at', 'tasks', [sa.text('created_at DESC')])

    # Create triggers
    if is_sqlite:
        # SQLite trigger
        op.execute("""
        CREATE TRIGGER update_tasks_updated_at AFTER UPDATE ON tasks
        BEGIN
            UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """)
    else:
        # Postgres trigger function and trigger
        op.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        op.execute("""
            CREATE TRIGGER update_tasks_updated_at
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'

    if is_sqlite:
        op.execute('DROP TRIGGER IF EXISTS update_tasks_updated_at')
    else:
        op.execute('DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks')
        op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop indexes
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_composite', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')

    # Drop table
    op.drop_table('tasks')
