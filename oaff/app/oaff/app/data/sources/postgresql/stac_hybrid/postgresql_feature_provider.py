from json import dumps
from typing import Final, List
from uuid import uuid4

import sqlalchemy as sa
from databases.core import Database

from oaff.app.data.retrieval.feature_provider import FeatureProvider
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_layer import PostgresqlLayer
from oaff.app.responses.models.collection_item_html import CollectionItemHtml
from oaff.app.responses.models.link import Link


class PostgresqlFeatureProvider(FeatureProvider):

    LINKS_PLACEHOLDER: Final = str(uuid4())

    def __init__(
        self,
        db: Database,
        layer: PostgresqlLayer,
    ):
        self.db = db
        self.layer = layer

    async def as_geojson(
        self,
        feature_id: str,
        links: List[Link],
    ) -> str:
        result = await self.db.fetch_one(
            # fmt: off
            sa.select([
                sa.text(f"""
                JSON_BUILD_OBJECT(
                    'type', 'Feature',
                    'id', "{self.layer.unique_field_name}",
                    'geometry', ST_AsGeoJSON(
                        "{self.layer.geometry_field_name}"
                    )::JSONB,
                    'properties', TO_JSONB({self.layer.table_name}) - '{
                        self.layer.unique_field_name
                    }' - '{
                        self.layer.geometry_field_name
                    }',
                    'links', '{self.LINKS_PLACEHOLDER}'
                )
                """)
            ]).select_from(
                self.layer.model
            ).where(self.get_clause(self.layer, feature_id))
            # fmt: on
        )
        return (
            result[0].replace(
                f'"{self.LINKS_PLACEHOLDER}"', dumps([dict(link) for link in links])
            )
            if result is not None
            else None
        )

    async def as_html_compatible(
        self,
        feature_id: str,
        links: List[Link],
    ) -> CollectionItemHtml:
        result = await self.db.fetch_one(
            sa.select(
                [
                    col
                    for col in self.layer.model.c
                    if col.name != self.layer.geometry_field_name
                ]
            )
            .select_from(self.layer.model)
            .where(self.get_clause(self.layer, feature_id))
        )
        return (
            CollectionItemHtml(
                collection_id=self.layer.id,
                feature_id=feature_id,
                format_links=links,
                properties={key: str(value) for key, value in dict(result).items()},
            )
            if result is not None
            else None
        )

    def get_clause(self, layer: PostgresqlLayer, feature_id: str):
        id_field = layer.model.columns[layer.unique_field_name]
        id_type = id_field.type.python_type
        if id_type is int:
            try:
                return id_field == int(feature_id)
            except ValueError:
                return False
        elif id_type is float:
            try:
                return id_field == float(feature_id)
            except ValueError:
                return False
        elif id_type is str:
            return id_field == feature_id
        else:
            return sa.cast(id_field, sa.types.String) == feature_id
