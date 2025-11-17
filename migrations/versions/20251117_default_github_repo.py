"""Set default GitHub repo for rulesets

Revision ID: 005_default_github_repo
Revises: 004_phase3_improvements
Create Date: 2025-11-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_default_github_repo'
down_revision = '004_phase3_improvements'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Set default GitHub repository URL for existing settings that don't have one
    """
    default_url = "https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/"

    # Update all existing settings where default_github_repo is NULL or empty
    op.execute(
        f"""
        UPDATE settings
        SET default_github_repo = '{default_url}'
        WHERE default_github_repo IS NULL OR default_github_repo = ''
        """
    )


def downgrade() -> None:
    """
    Revert default GitHub repository URL to NULL
    """
    default_url = "https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/"

    # Set back to NULL for settings that have the default value
    op.execute(
        f"""
        UPDATE settings
        SET default_github_repo = NULL
        WHERE default_github_repo = '{default_url}'
        """
    )
