"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables"""

    # Events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_code'), 'events', ['code'], unique=True)
    op.create_index(op.f('ix_events_is_active'), 'events', ['is_active'], unique=False)

    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_event_id'), 'roles', ['event_id'], unique=False)
    op.create_index(op.f('ix_roles_is_active'), 'roles', ['is_active'], unique=False)

    # Families table
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('contact_person', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_families_deleted_at'), 'families', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_families_email'), 'families', ['email'], unique=False)
    op.create_index(op.f('ix_families_event_id'), 'families', ['event_id'], unique=False)
    op.create_index(op.f('ix_families_is_active'), 'families', ['is_active'], unique=False)

    # Rulesets table
    op.create_table(
        'rulesets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rulesets_event_id'), 'rulesets', ['event_id'], unique=False)
    op.create_index(op.f('ix_rulesets_is_active'), 'rulesets', ['is_active'], unique=False)

    # Settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_name', sa.String(length=200), nullable=True),
        sa.Column('organization_address', sa.Text(), nullable=True),
        sa.Column('bank_account_holder', sa.String(length=200), nullable=True),
        sa.Column('bank_iban', sa.String(length=34), nullable=True),
        sa.Column('bank_bic', sa.String(length=11), nullable=True),
        sa.Column('invoice_subject_prefix', sa.String(length=100), nullable=True),
        sa.Column('invoice_footer_text', sa.Text(), nullable=True),
        sa.Column('default_github_repo', sa.String(length=200), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_event_id'), 'settings', ['event_id'], unique=True)

    # Participants table
    op.create_table(
        'participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('bildung_teilhabe_id', sa.String(length=100), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('medical_notes', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('calculated_price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('manual_price_override', sa.Float(), nullable=True),
        sa.Column('discount_percent', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('discount_reason', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('registration_date', sa.Date(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participants_deleted_at'), 'participants', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_participants_email'), 'participants', ['email'], unique=False)
    op.create_index(op.f('ix_participants_event_id'), 'participants', ['event_id'], unique=False)
    op.create_index(op.f('ix_participants_family_id'), 'participants', ['family_id'], unique=False)
    op.create_index(op.f('ix_participants_is_active'), 'participants', ['is_active'], unique=False)
    op.create_index(op.f('ix_participants_last_name'), 'participants', ['last_name'], unique=False)
    op.create_index(op.f('ix_participants_role_id'), 'participants', ['role_id'], unique=False)

    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('reference', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=True),
        sa.Column('family_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_event_id'), 'payments', ['event_id'], unique=False)
    op.create_index(op.f('ix_payments_family_id'), 'payments', ['family_id'], unique=False)
    op.create_index(op.f('ix_payments_participant_id'), 'payments', ['participant_id'], unique=False)

    # Expenses table
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('paid_by', sa.String(length=200), nullable=True),
        sa.Column('is_settled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('receipt_number', sa.String(length=100), nullable=True),
        sa.Column('receipt_file_path', sa.String(length=500), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expenses_event_id'), 'expenses', ['event_id'], unique=False)

    # Incomes table
    op.create_table(
        'incomes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('receipt_file_path', sa.String(length=500), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incomes_event_id'), 'incomes', ['event_id'], unique=False)
    op.create_index(op.f('ix_incomes_role_id'), 'incomes', ['role_id'], unique=False)

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_event_id'), 'tasks', ['event_id'], unique=False)
    op.create_index(op.f('ix_tasks_is_completed'), 'tasks', ['is_completed'], unique=False)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('tasks')
    op.drop_table('incomes')
    op.drop_table('expenses')
    op.drop_table('payments')
    op.drop_table('participants')
    op.drop_table('settings')
    op.drop_table('rulesets')
    op.drop_table('families')
    op.drop_table('roles')
    op.drop_table('events')
