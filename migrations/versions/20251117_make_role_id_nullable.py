"""Make role_id nullable in participants table

Revision ID: 002_role_id_nullable
Revises: 001_initial
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_role_id_nullable'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make role_id nullable in participants table"""

    # SQLite doesn't support ALTER COLUMN directly, so we need to check the database type
    # For SQLite: Create new table, copy data, drop old, rename new
    # For PostgreSQL: Use ALTER COLUMN

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'sqlite':
        # SQLite workaround: Can't modify column constraints easily
        # Instead, we'll use batch mode which recreates the table
        with op.batch_alter_table('participants', schema=None) as batch_op:
            batch_op.alter_column('role_id',
                                existing_type=sa.Integer(),
                                nullable=True)
    else:
        # PostgreSQL and other databases
        op.alter_column('participants', 'role_id',
                       existing_type=sa.Integer(),
                       nullable=True)


def downgrade() -> None:
    """Revert role_id back to non-nullable (requires data cleanup first!)"""

    bind = op.get_bind()
    dialect = bind.dialect.name

    # Note: This downgrade will fail if there are participants with NULL role_id
    # You would need to manually assign roles to all participants first

    if dialect == 'sqlite':
        with op.batch_alter_table('participants', schema=None) as batch_op:
            batch_op.alter_column('role_id',
                                existing_type=sa.Integer(),
                                nullable=False)
    else:
        op.alter_column('participants', 'role_id',
                       existing_type=sa.Integer(),
                       nullable=False)
