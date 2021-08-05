from json import dumps
from typing import Callable, Dict, Final, List
from uuid import uuid4

import sqlalchemy as sa
from databases.core import Database

from oaff.app.data.retrieval.feature_set_provider import FeatureSetProvider
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_layer import PostgresqlLayer
from oaff.app.responses.models.collection_items_html import CollectionItemsHtml
from oaff.app.responses.models.link import Link, PageLinkRel
from oaff.app.util import now_as_rfc3339


class PostgresqlFeatureSetProvider(FeatureSetProvider):

    FEATURES_PLACEHOLDER: Final = str(uuid4())

    def __init__(
        self,
        db: Database,
        id_set: sa.sql.expression.Select,
        layer: PostgresqlLayer,
        total_count: int,
    ):
        self.db = db
        self.id_set = id_set
        self.layer = layer
        self.total_count = total_count

    async def as_geojson(
        self,
        links: List[Link],
        page_links_provider: Callable[[int, int], Dict[PageLinkRel, Link]],
    ) -> str:
        rows = [
            row[0]
            for row in await self.db.fetch_all(
                # fmt: off
                sa.select([
                    sa.text(f"""
                    JSON_BUILD_OBJECT(
                        'type', 'Feature',
                        'id', source."{self.layer.unique_field_name}",
                        'geometry', ST_AsGeoJSON(
                            source."{self.layer.geometry_field_name}"
                        )::JSONB,
                        'properties', TO_JSONB(source) - '{
                            self.layer.unique_field_name
                        }' - '{
                            self.layer.geometry_field_name
                        }'
                    )
                    """)
                ])
                .select_from(
                    self.layer.model.alias("source").join(
                        self.id_set,
                        self.layer.model.alias("source").c[self.layer.unique_field_name]
                        == self.id_set.c["id"],
                    )
                )
                # fmt: on
            )
        ]
        return dumps(
            {
                "type": "FeatureCollection",
                "features": self.FEATURES_PLACEHOLDER,
                "links": [
                    dict(link)
                    for link in links
                    + list(page_links_provider(self.total_count, len(rows)).values())
                ],
                "numberMatched": self.total_count,
                "numberReturned": len(rows),
                "timeStamp": now_as_rfc3339(),
            }
        ).replace(f'"{self.FEATURES_PLACEHOLDER}"', f'[{",".join(rows)}]')

    async def as_html_compatible(
        self, links: List[Link], page_links_provider: Callable[[int, int], List[Link]]
    ) -> CollectionItemsHtml:
        rows = [
            dict(row)
            for row in await self.db.fetch_all(
                sa.select(
                    [
                        col
                        for col in self.layer.model.c
                        if col.name != self.layer.geometry_field_name
                    ]
                ).select_from(
                    self.layer.model.join(
                        self.id_set,
                        self.layer.model.primary_key.columns[self.layer.unique_field_name]
                        == self.id_set.c["id"],
                    )
                )
            )
        ]
        page_links = page_links_provider(self.total_count, len(rows))
        return CollectionItemsHtml(
            format_links=links,
            next_link=page_links[PageLinkRel.NEXT]
            if PageLinkRel.NEXT in page_links
            else None,
            prev_link=page_links[PageLinkRel.PREV]
            if PageLinkRel.PREV in page_links
            else None,
            features=rows,
            collection_id=self.layer.id,
            unique_field_name=self.layer.unique_field_name,
        )
