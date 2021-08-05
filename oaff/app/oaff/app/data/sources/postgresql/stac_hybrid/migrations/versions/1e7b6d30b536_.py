"""empty message
# flake8: noqa
Revision ID: 1e7b6d30b536
Revises: 0fda79152d26
Create Date: 2021-06-08 22:20:14.577127
"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from oaff.app.data.sources.postgresql.stac_hybrid import settings

# revision identifiers, used by Alembic.
revision = "1e7b6d30b536"
down_revision = "0fda79152d26"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "collections",
        sa.Column("id", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.TEXT(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("keywords", sa.ARRAY(sa.String(length=50)), nullable=True),
        sa.Column("license", sa.Text(), nullable=True),
        sa.Column("providers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("extent", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("temporal", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("schema_name", sa.String(length=63), nullable=False),
        sa.Column("table_name", sa.String(length=63), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("schema_name", "table_name"),
        sa.UniqueConstraint("title"),
        schema=settings.OAFF_SCHEMA_NAME,
    )


def downgrade():
    op.drop_table("collections", schema=settings.OAFF_SCHEMA_NAME)
