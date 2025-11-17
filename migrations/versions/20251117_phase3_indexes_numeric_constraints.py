"""Phase 3: Add indexes, convert Float to Numeric, add unique constraints

Revision ID: 004_phase3_improvements
Revises: 003_income_timestamps_ruleset_event_id
Create Date: 2025-11-17 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_phase3_improvements'
down_revision = '003_income_timestamps_ruleset_event_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Phase 3 Improvements:
    1. Add indexes to event_id in expense, payment, task tables
    2. Convert Float to Numeric(10, 2) for money fields
    3. Add unique constraint to settings.event_id
    """

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'sqlite':
        # SQLite: Use batch mode for table modifications

        # 1. Expense table: Add index to event_id and convert amount to Numeric
        with op.batch_alter_table('expenses', schema=None) as batch_op:
            batch_op.create_index('ix_expenses_event_id', ['event_id'], unique=False)
            batch_op.alter_column('amount',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(10, 2),
                                existing_nullable=False)

        # 2. Payment table: Add index to event_id and convert amount to Numeric
        with op.batch_alter_table('payments', schema=None) as batch_op:
            batch_op.create_index('ix_payments_event_id', ['event_id'], unique=False)
            batch_op.alter_column('amount',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(10, 2),
                                existing_nullable=False)

        # 3. Income table: Convert amount to Numeric
        with op.batch_alter_table('incomes', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(10, 2),
                                existing_nullable=False)

        # 4. Participant table: Convert price fields to Numeric
        with op.batch_alter_table('participants', schema=None) as batch_op:
            batch_op.alter_column('calculated_price',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(10, 2),
                                existing_nullable=False)
            batch_op.alter_column('manual_price_override',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(10, 2),
                                existing_nullable=True)
            batch_op.alter_column('discount_percent',
                                existing_type=sa.Float(),
                                type_=sa.Numeric(5, 2),
                                existing_nullable=False)

        # 5. Task table: Add index to event_id
        with op.batch_alter_table('tasks', schema=None) as batch_op:
            batch_op.create_index('ix_tasks_event_id', ['event_id'], unique=False)

        # 6. Settings table: Add unique constraint to event_id
        with op.batch_alter_table('settings', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_settings_event_id', ['event_id'])

    else:
        # PostgreSQL and other databases

        # 1. Add indexes
        op.create_index('ix_expenses_event_id', 'expenses', ['event_id'], unique=False)
        op.create_index('ix_payments_event_id', 'payments', ['event_id'], unique=False)
        op.create_index('ix_tasks_event_id', 'tasks', ['event_id'], unique=False)

        # 2. Convert Float to Numeric
        op.alter_column('expenses', 'amount',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(10, 2),
                       existing_nullable=False)

        op.alter_column('payments', 'amount',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(10, 2),
                       existing_nullable=False)

        op.alter_column('incomes', 'amount',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(10, 2),
                       existing_nullable=False)

        op.alter_column('participants', 'calculated_price',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(10, 2),
                       existing_nullable=False)

        op.alter_column('participants', 'manual_price_override',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(10, 2),
                       existing_nullable=True)

        op.alter_column('participants', 'discount_percent',
                       existing_type=sa.Float(),
                       type_=sa.Numeric(5, 2),
                       existing_nullable=False)

        # 3. Add unique constraint
        op.create_unique_constraint('uq_settings_event_id', 'settings', ['event_id'])


def downgrade() -> None:
    """
    Revert Phase 3 improvements
    """

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'sqlite':
        # SQLite: Use batch mode

        with op.batch_alter_table('settings', schema=None) as batch_op:
            batch_op.drop_constraint('uq_settings_event_id', type_='unique')

        with op.batch_alter_table('tasks', schema=None) as batch_op:
            batch_op.drop_index('ix_tasks_event_id')

        with op.batch_alter_table('participants', schema=None) as batch_op:
            batch_op.alter_column('discount_percent',
                                existing_type=sa.Numeric(5, 2),
                                type_=sa.Float(),
                                existing_nullable=False)
            batch_op.alter_column('manual_price_override',
                                existing_type=sa.Numeric(10, 2),
                                type_=sa.Float(),
                                existing_nullable=True)
            batch_op.alter_column('calculated_price',
                                existing_type=sa.Numeric(10, 2),
                                type_=sa.Float(),
                                existing_nullable=False)

        with op.batch_alter_table('incomes', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                existing_type=sa.Numeric(10, 2),
                                type_=sa.Float(),
                                existing_nullable=False)

        with op.batch_alter_table('payments', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                existing_type=sa.Numeric(10, 2),
                                type_=sa.Float(),
                                existing_nullable=False)
            batch_op.drop_index('ix_payments_event_id')

        with op.batch_alter_table('expenses', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                existing_type=sa.Numeric(10, 2),
                                type_=sa.Float(),
                                existing_nullable=False)
            batch_op.drop_index('ix_expenses_event_id')

    else:
        # PostgreSQL and other databases
        op.drop_constraint('uq_settings_event_id', 'settings', type_='unique')

        op.drop_index('ix_tasks_event_id', table_name='tasks')
        op.drop_index('ix_payments_event_id', table_name='payments')
        op.drop_index('ix_expenses_event_id', table_name='expenses')

        op.alter_column('participants', 'discount_percent',
                       existing_type=sa.Numeric(5, 2),
                       type_=sa.Float(),
                       existing_nullable=False)

        op.alter_column('participants', 'manual_price_override',
                       existing_type=sa.Numeric(10, 2),
                       type_=sa.Float(),
                       existing_nullable=True)

        op.alter_column('participants', 'calculated_price',
                       existing_type=sa.Numeric(10, 2),
                       type_=sa.Float(),
                       existing_nullable=False)

        op.alter_column('incomes', 'amount',
                       existing_type=sa.Numeric(10, 2),
                       type_=sa.Float(),
                       existing_nullable=False)

        op.alter_column('payments', 'amount',
                       existing_type=sa.Numeric(10, 2),
                       type_=sa.Float(),
                       existing_nullable=False)

        op.alter_column('expenses', 'amount',
                       existing_type=sa.Numeric(10, 2),
                       type_=sa.Float(),
                       existing_nullable=False)
