from datetime import date, datetime
from hashlib import sha256
from logging import getLogger
from os import path
from typing import Any, Awaitable, Callable, Dict, Final, List, Type

# geoalchemy import required for sa.MetaData reflection, even though unused in module
import geoalchemy2 as ga  # noqa: F401
import sqlalchemy as sa  # type: ignore
from alembic import command
from alembic.config import Config
from databases import Database
from pygeofilter.ast import Node
from pygeofilter.backends.sqlalchemy import to_filter as node_to_sqlalchemy
from pytz import timezone

from oaff.app.data.retrieval.feature_provider import FeatureProvider
from oaff.app.data.retrieval.feature_set_provider import FeatureSetProvider
from oaff.app.data.retrieval.item_constraints import ItemConstraints
from oaff.app.data.sources.common.data_source import DataSource
from oaff.app.data.sources.common.temporal import (
    TemporalDeclaration,
    TemporalInstant,
    TemporalRange,
)
from oaff.app.data.sources.postgresql import settings
from oaff.app.data.sources.postgresql.stac_hybrid.models.collections import collections
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_feature_provider import (
    PostgresqlFeatureProvider,
)
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_feature_set_provider import (  # noqa: E501
    PostgresqlFeatureSetProvider,
)
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_layer import PostgresqlLayer
from oaff.app.data.sources.postgresql.stac_hybrid.settings import (
    blacklist,
    manage_as_collections,
    whitelist,
)
from oaff.app.settings import SPATIAL_FILTER_GEOMETRY_FIELD_ALIAS
from oaff.app.util import datetime_as_rfc3339

LOGGER: Final = getLogger(__file__)
METADATA: Final = sa.MetaData()


class PostgresqlDataSource(DataSource):

    DATA_SOURCE_NAME: Final = "postgresql-hybrid"

    def __init__(
        self,
        connection_name: str,
        connection_tester: Callable[[Database, str], Awaitable[None]],
    ):
        super().__init__(f"{self.DATA_SOURCE_NAME}:{connection_name}")
        self.db = Database(settings.url(connection_name))
        self.connection_name = connection_name
        self.connection_tester = connection_tester

    async def initialize(self) -> None:
        try:
            self.default_tz = timezone(settings.default_tz_code(self.connection_name))
        except Exception as e:
            LOGGER.error(
                "".join(
                    [
                        f"default tz invalid for {self.connection_name}: ",
                        f"{self.default_tz_code} ({e})",
                    ]
                )
            )
            raise e
        await self.connection_tester(self.db, self.connection_name)
        if manage_as_collections(self.connection_name):
            LOGGER.info("Running Alembic migrations")
            alembic_cfg = Config()
            alembic_cfg.set_main_option(
                "script_location", path.join(path.dirname(__file__), "migrations")
            )
            alembic_cfg.set_main_option("sqlalchemy.url", str(self.db.url))
            command.upgrade(alembic_cfg, "head")
            LOGGER.info("Alembic migrations complete")
        else:
            LOGGER.info(f"Not managing {self.connection_name} via Alembic")

    async def get_layers(self) -> List[PostgresqlLayer]:
        derived_layers = await self._get_derived_layers()
        if manage_as_collections(self.connection_name):

            def get_if_available(
                source: Dict[str, Any], properties: List[str], default: Any
            ) -> Any:
                getter = source
                for i in range(len(properties)):
                    if properties[i] not in getter or getter[properties[i]] is None:
                        return default
                    else:
                        getter = getter[properties[i]]

                return getter

            merged_layers = derived_layers.copy()
            for collection in [
                dict(db_value)
                for db_value in await self.db.fetch_all(collections.select())
            ]:
                key = f"{collection['schema_name']}.{collection['table_name']}"
                if key not in merged_layers:
                    continue
                merged_layers[key].id = collection["id"]
                merged_layers[key].title = get_if_available(
                    collection, ["title"], merged_layers[key].title
                )
                merged_layers[key].description = get_if_available(
                    collection, ["description"], merged_layers[key].description
                )
                merged_layers[key].bboxes = get_if_available(
                    collection, ["extent", "spatial", "bbox"], merged_layers[key].bboxes
                )
                merged_layers[key].intervals = get_if_available(
                    collection,
                    ["extent", "temporal", "interval"],
                    merged_layers[key].intervals,
                )
                merged_layers[key].temporal_attributes = (
                    [
                        self._temporal_field_to_declaration(
                            field,
                            {
                                field.field_name: field
                                for field in derived_layers[key].temporal_attributes
                            },
                        )
                        for field in collection["temporal"]
                    ]
                    if collection["temporal"] is not None
                    else merged_layers[key].temporal_attributes
                )
                merged_layers[key].license = get_if_available(
                    collection, ["license"], merged_layers[key].license
                )
                merged_layers[key].keywords = get_if_available(
                    collection, ["keywords"], merged_layers[key].keywords
                )
                merged_layers[key].providers = get_if_available(
                    collection, ["providers"], merged_layers[key].providers
                )
            layers = list(merged_layers.values())
        else:
            layers = list(derived_layers.values())

        return layers

    async def get_feature_set_provider(
        self,
        layer: PostgresqlLayer,
        constraints: ItemConstraints,
        ast: Type[Node] = None,
    ) -> Type[FeatureSetProvider]:
        filters = (
            node_to_sqlalchemy(
                ast,
                {
                    SPATIAL_FILTER_GEOMETRY_FIELD_ALIAS: layer.model.c[
                        layer.geometry_field_name
                    ],
                    **{
                        field_name: layer.model.c[field_name]
                        for field_name in layer.fields
                    },
                },
            )
            if ast is not None
            else 1 == 1
        )
        id_set = (
            sa.select(
                [layer.model.primary_key.columns[layer.unique_field_name].label("id")]
            )
            .select_from(layer.model)
            .where(filters)
            .limit(constraints.limit)
            .offset(constraints.offset)
            .order_by(layer.unique_field_name)
            .alias("id_set")
        )
        total_count = (
            await self.db.fetch_one(
                sa.select([sa.func.count()]).select_from(layer.model).where(filters)
            )
        )[0]

        return PostgresqlFeatureSetProvider(self.db, id_set, layer, total_count)

    async def get_feature_provider(
        self,
        layer: PostgresqlLayer,
    ) -> Type[FeatureProvider]:
        return PostgresqlFeatureProvider(self.db, layer)

    async def get_crs_identifier(self, layer: PostgresqlLayer) -> Any:
        return layer.geometry_srid

    async def disconnect(self) -> None:
        if self.db.is_connected:
            await self.db.disconnect()

    async def _get_derived_layers(self) -> Dict[str, PostgresqlLayer]:
        tables = await self._get_compatible_tables()
        table_spatial_extents = await self._get_table_spatial_extents(tables)
        table_models = await self._get_table_sqlalchemy_models(tables)
        table_temporal_fields = await self._get_table_temporal_fields(table_models)
        table_temporal_extents = await self._get_table_temporal_extents(
            table_models,
            table_temporal_fields,
        )
        layers = {
            qualified_layer_name: PostgresqlLayer(
                id=self._id_generator(qualified_layer_name),
                title=tables[qualified_layer_name]["table_name"],
                description=None,
                bboxes=[table_spatial_extents[qualified_layer_name]],
                intervals=table_temporal_extents[qualified_layer_name]
                if qualified_layer_name in table_temporal_extents
                else [None, None],
                data_source_id=self.id,
                schema_name=tables[qualified_layer_name]["schema_name"],
                table_name=tables[qualified_layer_name]["table_name"],
                model=table_models[qualified_layer_name],
                geometry_field_name=tables[qualified_layer_name]["geometry_field"],
                geometry_srid=tables[qualified_layer_name]["srid"],
                geometry_crs_auth_name=tables[qualified_layer_name]["auth_name"],
                geometry_crs_auth_code=tables[qualified_layer_name]["auth_code"],
                temporal_attributes=table_temporal_fields[qualified_layer_name],
                license=None,
                keywords=None,
                providers=None,
            )
            for qualified_layer_name in tables.keys()
        }

        return layers

    def _id_generator(self, qualified_layer_name: str) -> str:
        return sha256(
            "/".join(
                [
                    self.connection_name or "",
                    qualified_layer_name,
                ]
            ).encode("UTF-8")
        ).hexdigest()

    def _temporal_field_to_declaration(
        self,
        field: Dict[str, str],
        derived_attributes: Dict[str, TemporalDeclaration],
    ) -> Type[TemporalDeclaration]:
        if field["type"] == "range":
            derived_start = derived_attributes[field["start_field"]]
            derived_end = derived_attributes[field["end_field"]]
            return TemporalRange(
                start_field_name=derived_start.field_name,
                start_tz_aware=derived_start.field_tz_aware,
                end_field_name=derived_end.field_name,
                end_tz_aware=derived_end.field_tz_aware,
                tz=self.default_tz,
            )
        elif field["type"] == "instant":
            derived_field = derived_attributes[field["field"]]
            return TemporalInstant(
                field_name=derived_field.field_name,
                field_tz_aware=derived_field.field_tz_aware,
                tz=self.default_tz,
            )
        else:
            raise ValueError(f"Unknown temporal type {field['type']}")

    async def _get_compatible_tables(self) -> Dict[str, Dict[str, Any]]:
        sql = None
        with open(path.join(path.dirname(__file__), "sql", "layers.sql")) as sql_file:
            sql = sql_file.read()
        return {
            row["qualified_table_name"]: row
            for row in [dict(db_value) for db_value in await self.db.fetch_all(sql)]
            if self._table_supported(row) and self._table_permitted(row)
        }

    def _table_permitted(self, row: Dict[str, Any]) -> bool:
        whitelisted = whitelist(self.connection_name)
        blacklisted = blacklist(self.connection_name)
        qualified_layer_name = row["qualified_table_name"]
        if len(whitelisted) > 0 and len(blacklisted) > 0:
            LOGGER.warning(
                "layer whitelist and blacklist are both defined, "
                "neither will be applied. Only one should be defined"
            )
            return True

        permitted = False
        if len(whitelisted) > 0:
            permitted = qualified_layer_name in whitelisted
        elif len(blacklisted) > 0:
            permitted = qualified_layer_name not in blacklisted
        else:
            permitted = True
        if not permitted:
            LOGGER.info(f"{qualified_layer_name} not permitted by blacklist/whitelist")
        return permitted

    def _table_supported(self, row: Dict[str, Any]) -> bool:
        exclude_reason = row["exclude_reason"]
        if exclude_reason is None:
            return True
        else:
            LOGGER.info(f"{row['qualified_table_name']} not supported: {exclude_reason}")

    async def _get_table_spatial_extents(
        self, tables: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[float]]:
        table_spatial_extents = dict()
        for table_info in tables.values():
            extents = await self.db.fetch_one(
                f"""
                WITH extents AS (
                  SELECT ST_TRANSFORM(
                           ST_SetSRID(
                             ST_MakePoint(
                               MIN(ST_XMIN({table_info["geometry_field"]}::geometry)),
                               MIN(ST_YMIN({table_info["geometry_field"]}::geometry))
                             ), {table_info["srid"]}
                           ), 4326
                         ) ll
                       , ST_TRANSFORM(
                           ST_SetSRID(
                             ST_MakePoint(
                               MAX(ST_XMAX({table_info["geometry_field"]}::geometry)),
                               MAX(ST_YMAX({table_info["geometry_field"]}::geometry))
                             ), {table_info["srid"]}
                           ), 4326
                         ) ur
                    FROM {table_info["schema_name"]}.{table_info["table_name"]}
                )
                SELECT ST_X(ll) x_min
                     , ST_Y(ll) y_min
                     , ST_X(ur) x_max
                     , ST_Y(ur) y_max
                  FROM extents
                ;
                """
            )
            if (
                extents is not None
                and len(list(filter(lambda value: value is not None, extents.values())))
                == 4
            ):
                table_spatial_extents[table_info["qualified_table_name"]] = list(
                    extents.values()
                )
            else:
                table_spatial_extents[table_info["qualified_table_name"]] = [
                    -180,
                    -90,
                    180,
                    90,
                ]

        return table_spatial_extents

    async def _get_table_sqlalchemy_models(
        self, tables: Dict[str, Dict[str, Any]]
    ) -> Dict[str, sa.Table]:
        table_models = {}
        metadata_by_schema = {}
        temp_engine = sa.create_engine(str(self.db.url))
        for qualified_table_name, table_info in tables.items():
            schema_name = table_info["schema_name"]
            if schema_name not in metadata_by_schema:
                metadata_by_schema[schema_name] = sa.MetaData(
                    bind=temp_engine, schema=schema_name
                )
                metadata_by_schema[schema_name].reflect()
            table_models[qualified_table_name] = metadata_by_schema[schema_name].tables[
                qualified_table_name
            ]
        temp_engine.dispose()

        return table_models

    async def _get_table_temporal_fields(
        self, table_models: Dict[str, sa.Table]
    ) -> Dict[str, List[TemporalInstant]]:
        return {
            qualified_table_name: [
                TemporalInstant(
                    field_name=column.name,
                    field_tz_aware=column.type.timezone
                    if isinstance(column.type, sa.dialects.postgresql.TIMESTAMP)
                    else False,
                    tz=self.default_tz,
                )
                for column in model.columns
                if column.type.__class__
                in [
                    sa.dialects.postgresql.TIMESTAMP,
                    sa.dialects.postgresql.DATE,
                ]
            ]
            for qualified_table_name, model in table_models.items()
        }

    async def _get_table_temporal_extents(  # noqa: C901
        self,
        table_models: Dict[str, sa.Table],
        table_temporal_fields: Dict[str, List[TemporalInstant]],
    ) -> Dict[str, List[List[datetime]]]:
        table_temporal_extents = {}  # type: ignore
        for qualified_table_name, temporal_fields in table_temporal_fields.items():
            start = None
            end = None
            if qualified_table_name not in table_temporal_extents:
                table_temporal_extents[qualified_table_name] = []
            for temporal_field in temporal_fields:
                range_row = await self.db.fetch_one(
                    sa.select(
                        [
                            sa.func.min(
                                table_models[qualified_table_name].columns[
                                    temporal_field.field_name
                                ]
                            ),
                            sa.func.max(
                                table_models[qualified_table_name].columns[
                                    temporal_field.field_name
                                ]
                            ),
                        ]
                    ).select_from(table_models[qualified_table_name])
                )
                row_start, row_end = range_row[0], range_row[1]
                if row_start is not None:
                    if isinstance(row_start, datetime):
                        if row_start.tzinfo is None:
                            # explicitly set TIMESTAMP WITHOUT TIME ZONE to the database
                            # time zone so that they can be compared to time-zone aware
                            # TIMESTAMPTZ and be converted to other time zones
                            row_start = self.default_tz.localize(row_start)
                    elif isinstance(row_start, date):
                        row_start = self.default_tz.localize(
                            datetime(row_start.year, row_start.month, row_start.day)
                        )
                    if start is None or start > row_start:
                        start = row_start
                if row_end is not None:
                    if isinstance(row_end, datetime):
                        if row_end.tzinfo is None:
                            row_end = self.default_tz.localize(row_end)
                    elif isinstance(row_end, date):
                        row_end = self.default_tz.localize(
                            datetime(
                                row_end.year,
                                row_end.month,
                                row_end.day,
                            )
                        )
                    if end is None or end < row_end:
                        end = row_end

            table_temporal_extents[qualified_table_name].append(
                [
                    datetime_as_rfc3339(start),
                    datetime_as_rfc3339(end),
                ]
            )

        return table_temporal_extents
