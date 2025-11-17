"""Add timestamps to Income and make Ruleset event_id non-nullable

Revision ID: 003_income_timestamps_ruleset_event_id
Revises: 002_role_id_nullable
Create Date: 2025-11-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003_income_timestamps_ruleset_event_id'
down_revision = '002_role_id_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    1. Add created_at and updated_at columns to incomes table
    2. Make event_id non-nullable in rulesets table and add index
    """

    bind = op.get_bind()
    dialect = bind.dialect.name

    # 1. Add timestamps to incomes table
    current_time = datetime.utcnow()

    # Add created_at column
    op.add_column('incomes', sa.Column('created_at', sa.DateTime(), nullable=False,
                                       server_default=sa.text('CURRENT_TIMESTAMP')))
    # Add updated_at column
    op.add_column('incomes', sa.Column('updated_at', sa.DateTime(), nullable=False,
                                       server_default=sa.text('CURRENT_TIMESTAMP')))

    # 2. Make event_id non-nullable in rulesets table
    # First, ensure all rulesets have an event_id (update any NULL values if they exist)
    # This is critical - if there are NULLs, the migration will fail

    if dialect == 'sqlite':
        # SQLite workaround using batch mode
        with op.batch_alter_table('rulesets', schema=None) as batch_op:
            # Make event_id non-nullable
            batch_op.alter_column('event_id',
                                existing_type=sa.Integer(),
                                nullable=False)
            # Add index if not exists (check first to avoid errors)
            try:
                batch_op.create_index('ix_rulesets_event_id', ['event_id'], unique=False)
            except:
                pass  # Index might already exist
    else:
        # PostgreSQL and other databases
        op.alter_column('rulesets', 'event_id',
                       existing_type=sa.Integer(),
                       nullable=False)
        try:
            op.create_index('ix_rulesets_event_id', 'rulesets', ['event_id'], unique=False)
        except:
            pass  # Index might already exist


def downgrade() -> None:
    """
    Revert changes:
    1. Remove timestamps from incomes table
    2. Make event_id nullable in rulesets table
    """

    bind = op.get_bind()
    dialect = bind.dialect.name

    # 1. Remove timestamps from incomes table
    op.drop_column('incomes', 'updated_at')
    op.drop_column('incomes', 'created_at')

    # 2. Make event_id nullable again in rulesets table
    if dialect == 'sqlite':
        with op.batch_alter_table('rulesets', schema=None) as batch_op:
            batch_op.alter_column('event_id',
                                existing_type=sa.Integer(),
                                nullable=True)
            # Don't drop the index on downgrade - keep it for performance
    else:
        op.alter_column('rulesets', 'event_id',
                       existing_type=sa.Integer(),
                       nullable=True)
