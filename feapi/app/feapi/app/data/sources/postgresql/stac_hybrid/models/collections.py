import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from feapi.app.data.sources.postgresql.stac_hybrid.settings import FEAPI_METADATA

collections = sa.Table(
    "collections",
    FEAPI_METADATA,
    sa.Column("id", sa.types.String(1024), primary_key=True),
    sa.Column("title", sa.types.TEXT, nullable=False, unique=True),
    sa.Column("description", sa.types.Text),
    sa.Column("keywords", sa.types.ARRAY(sa.types.String(50))),
    sa.Column("license", sa.types.Text),
    sa.Column("providers", JSONB),
    sa.Column("extent", JSONB),
    sa.Column("temporal", JSONB),
    sa.Column("schema_name", sa.String(63), nullable=False),
    sa.Column("table_name", sa.String(63), nullable=False),
    sa.UniqueConstraint("schema_name", "table_name"),
)
