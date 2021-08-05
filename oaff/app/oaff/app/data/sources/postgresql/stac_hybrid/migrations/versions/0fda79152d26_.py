"""empty message
# flake8: noqa
Revision ID: 0fda79152d26
Revises: 
Create Date: 2021-06-03 18:39:28.737450
"""
from alembic import op

from oaff.app.data.sources.postgresql.stac_hybrid import settings

# revision identifiers, used by Alembic.
revision = "0fda79152d26"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.OAFF_SCHEMA_NAME}")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade():
    # don't drop schema or extension on downgrade
    # no guarantee that we created them in upgrade
    pass
