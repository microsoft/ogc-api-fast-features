from datetime import datetime
from os import environ
from typing import Final, List, Optional

from feapi.app.data.sources.postgresql.settings import name_to_suffix
from feapi.app.settings import ENV_VAR_PREFIX
from feapi.testing.data.load.db import update_db

table_mply_4326: Final = "mply_4326"
table_pnt_4326: Final = "pnt_4326"
table_pnt_3857: Final = "pnt_3857"
table_pnt_4326_1_instant_utc: Final = "pnt_4326_1_instant_utc"
table_pnt_4326_2_instants_utc: Final = "pnt_4326_2_instants_utc"
table_pnt_4326_1_instant_local: Final = "pnt_4326_1_instant_local"
table_pnt_4326_2_instants_local: Final = "pnt_4326_2_instants_local"
table_pnt_4326_2_instants_mixed: Final = "pnt_4326_2_instants_mixed"
table_pnt_4326_4_instants_utc: Final = "pnt_4326_4_instants_utc"
table_pnt_4326_4_instants_local: Final = "pnt_4326_4_instants_local"
table_pnt_4326_4_instants_mixed: Final = "pnt_4326_4_instants_mixed"
table_pnt_4326_1_date: Final = "pnt_4326_1_date"
table_pnt_4326_2_dates: Final = "pnt_4326_2_dates"
table_pnt_4326_1_date_1_instant: Final = "pnt_4326_1_date_1_instant"
table_pnt_4326_float_id: Final = "pnt_4326_float_id"
table_pnt_4326_str_id: Final = "pnt_4326_str_id"
table_pnt_geog: Final = "pnt_geog"

tables: Final = {
    table_mply_4326: f"""
    CREATE TABLE IF NOT EXISTS {table_mply_4326} (
            id SERIAL PRIMARY KEY
    ,     name VARCHAR(100) NOT NULL UNIQUE
    , boundary GEOMETRY(MULTIPOLYGON, 4326) NOT NULL
    )
    """,
    table_pnt_4326: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326} (
            id SERIAL PRIMARY KEY
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_3857: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_3857} (
            id SERIAL PRIMARY KEY
    ,     name VARCHAR(100)
    , location GEOMETRY(POINT, 3857) NOT NULL
    )
    """,
    table_pnt_4326_1_instant_utc: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_1_instant_utc} (
                id SERIAL PRIMARY KEY
    , createdts TIMESTAMPTZ
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_2_instants_utc: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_2_instants_utc} (
            id SERIAL PRIMARY KEY
    ,  startts TIMESTAMPTZ
    ,    endts TIMESTAMPTZ
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_1_instant_local: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_1_instant_local} (
                id SERIAL PRIMARY KEY
    , createdts TIMESTAMP
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_2_instants_local: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_2_instants_local} (
                id SERIAL PRIMARY KEY
    ,   startts TIMESTAMP
    ,     endts TIMESTAMP
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_2_instants_mixed: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_2_instants_mixed} (
                id SERIAL PRIMARY KEY
    ,   startts TIMESTAMPTZ
    ,     endts TIMESTAMP
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_1_date: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_1_date} (
                id SERIAL PRIMARY KEY
    ,   created DATE
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_2_dates: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_2_dates} (
                id SERIAL PRIMARY KEY
    ,    startd DATE
    ,      endd DATE
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_1_date_1_instant: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_1_date_1_instant} (
                id SERIAL PRIMARY KEY
    ,   startts TIMESTAMPTZ
    ,      endd DATE
    ,  location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_4_instants_utc: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_4_instants_utc} (
            id SERIAL PRIMARY KEY
    , startts1 TIMESTAMPTZ
    ,   endts1 TIMESTAMPTZ
    , startts2 TIMESTAMPTZ
    ,   endts2 TIMESTAMPTZ
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_4_instants_local: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_4_instants_local} (
            id SERIAL PRIMARY KEY
    , startts1 TIMESTAMP
    ,   endts1 TIMESTAMP
    , startts2 TIMESTAMP
    ,   endts2 TIMESTAMP
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_4_instants_mixed: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_4_instants_mixed} (
            id SERIAL PRIMARY KEY
    , startts1 TIMESTAMPTZ
    ,   endts1 TIMESTAMP
    , startts2 TIMESTAMPTZ
    ,   endts2 TIMESTAMP
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_float_id: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_float_id} (
            id DOUBLE PRECISION PRIMARY KEY
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_4326_str_id: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_4326_str_id} (
            id TEXT PRIMARY KEY
    , location GEOMETRY(POINT, 4326) NOT NULL
    )
    """,
    table_pnt_geog: f"""
    CREATE TABLE IF NOT EXISTS {table_pnt_geog} (
            id TEXT PRIMARY KEY
    , location GEOGRAPHY(POINT, 4326) NOT NULL
    )
    """,
}


temporal_config: Final = {
    table_pnt_4326_2_instants_utc: '[{"type": "range", "start_field": "startts", "end_field": "endts"}]',  # noqa: E501
    table_pnt_4326_4_instants_utc: '[{"type": "range", "start_field": "startts1", "end_field": "endts1"}, {"type": "range", "start_field": "startts2", "end_field": "endts2"}]',  # noqa: E501
    table_pnt_4326_4_instants_local: '[{"type": "range", "start_field": "startts1", "end_field": "endts1"}, {"type": "range", "start_field": "startts2", "end_field": "endts2"}]',  # noqa: E501
    table_pnt_4326_4_instants_mixed: '[{"type": "range", "start_field": "startts1", "end_field": "endts1"}, {"type": "range", "start_field": "startts2", "end_field": "endts2"}]',  # noqa: E501
    table_pnt_4326_2_instants_local: '[{"type": "range", "start_field": "startts", "end_field": "endts"}]',  # noqa: E501
    table_pnt_4326_2_instants_mixed: '[{"type": "range", "start_field": "startts", "end_field": "endts"}]',  # noqa: E501
    table_pnt_4326_1_date: '[{"type": "instant", "field": "created"}]',
    table_pnt_4326_2_dates: '[{"type": "range", "start_field": "startd", "end_field": "endd"}]',  # noqa: E501
    table_pnt_4326_1_instant_utc: '[{"type": "instant", "field": "createdts"}]',  # noqa: E501
}


def create_common(source_name, table_names: Optional[List[str]] = None):
    for sql in (
        [value for key, value in tables.items() if key in table_names]
        if table_names is not None
        else tables.values()
    ):
        update_db(
            sql,
            source_name,
        )


def drop_common(source_name):
    for table_name in tables.keys():
        update_db(f"DROP TABLE IF EXISTS {table_name}", source_name)


def truncate_common(source_name, table_names: Optional[List[str]] = None):
    for table_name in table_names or tables.keys():
        update_db(f"TRUNCATE TABLE {table_name}", source_name)


def insert_table_mply_4326_basic(source_name):
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('boundary 01', ST_GeomFromText('MULTIPOLYGON (((
            0 0, 0 1, 1 1, 1 0, 0 0
        )))', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_basic(source_name):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326} (location) VALUES
        (ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_1_instant_utc_with(
    source_name, dt: Optional[datetime], point_wkt: Optional[str] = "POINT(0 1)"
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_1_instant_utc} (createdts, location) VALUES
        ({_datetime_to_ts_insert(dt)}, ST_GeomFromText('{point_wkt}', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_2_instants_utc_with(
    source_name, dtstart: Optional[datetime], dtend: Optional[datetime]
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_2_instants_utc} (startts, endts, location) VALUES
        (
            {_datetime_to_ts_insert(dtstart)}
          , {_datetime_to_ts_insert(dtend)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_1_instant_local_with(source_name, dt: Optional[datetime]):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_1_instant_local} (createdts, location) VALUES
        ({_datetime_to_ts_insert(dt, False)}, ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_2_instants_local_with(
    source_name, dtstart: Optional[datetime], dtend: Optional[datetime]
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_2_instants_local} (startts, endts, location) VALUES
        (
            {_datetime_to_ts_insert(dtstart, False)}
          , {_datetime_to_ts_insert(dtend, False)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_2_instants_mixed_with(
    source_name, dtstart: Optional[datetime], dtend: Optional[datetime]
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_2_instants_mixed} (startts, endts, location) VALUES
        (
            {_datetime_to_ts_insert(dtstart)}
          , {_datetime_to_ts_insert(dtend, False)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_4_instants_utc_with(
    source_name,
    dtstart1: Optional[datetime],
    dtend1: Optional[datetime],
    dtstart2: Optional[datetime],
    dtend2: Optional[datetime],
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_4_instants_utc} (
            startts1, endts1, startts2, endts2, location
        ) VALUES
        (
            {_datetime_to_ts_insert(dtstart1)}
          , {_datetime_to_ts_insert(dtend1)}
          , {_datetime_to_ts_insert(dtstart2)}
          , {_datetime_to_ts_insert(dtend2)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_4_instants_local_with(
    source_name,
    dtstart1: Optional[datetime],
    dtend1: Optional[datetime],
    dtstart2: Optional[datetime],
    dtend2: Optional[datetime],
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_4_instants_local} (
            startts1, endts1, startts2, endts2, location
        ) VALUES
        (
            {_datetime_to_ts_insert(dtstart1, False)}
          , {_datetime_to_ts_insert(dtend1, False)}
          , {_datetime_to_ts_insert(dtstart2, False)}
          , {_datetime_to_ts_insert(dtend2, False)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_4_instants_mixed_with(
    source_name,
    dtstart1: Optional[datetime],
    dtend1: Optional[datetime],
    dtstart2: Optional[datetime],
    dtend2: Optional[datetime],
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_4_instants_mixed} (
            startts1, endts1, startts2, endts2, location
        ) VALUES
        (
            {_datetime_to_ts_insert(dtstart1)}
          , {_datetime_to_ts_insert(dtend1, False)}
          , {_datetime_to_ts_insert(dtstart2)}
          , {_datetime_to_ts_insert(dtend2, False)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_1_date_with(source_name, date: Optional[datetime]):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_1_date} (created, location) VALUES
        (
            {_datetime_to_date_insert(date)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_2_dates_with(
    source_name, start: Optional[datetime], end: Optional[datetime]
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_2_dates} (startd, endd, location) VALUES
        (
            {_datetime_to_date_insert(start)}
          , {_datetime_to_date_insert(end)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_1_date_1_instant_with(
    source_name, startts: Optional[datetime], endd: Optional[datetime]
):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_1_date_1_instant} (startts, endd, location) VALUES
        (
            {_datetime_to_ts_insert(startts)}
          , {_datetime_to_date_insert(endd)}
          , ST_GeomFromText('POINT(0 1)', 4326))
        """,
        source_name,
    )


def insert_table_pnt_4326_float_id_with(source_name: str, id: float):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_float_id} (id, location) VALUES
        (
            {id}
          , ST_GeomFromText('POINT(0 1)', 4326)
        )
        """,
        source_name,
    )


def insert_table_pnt_4326_str_id_with(source_name: str, id: str):
    update_db(
        f"""
        INSERT INTO {table_pnt_4326_str_id} (id, location) VALUES
        (
            '{id}'
          , ST_GeomFromText('POINT(0 1)', 4326)
        )
        """,
        source_name,
    )


def insert_table_pnt_geog_with(source_name: str, id: str):
    update_db(
        f"""
        INSERT INTO {table_pnt_geog} (id, location) VALUES
        (
            '{id}'
          , ST_GeogFromText('POINT(0 1)', 4326)
        )
        """
    )


def update_db_timezone(source_name: str, tz_name: str) -> None:
    environ_key = f"{ENV_VAR_PREFIX}POSTGRESQL_DEFAULT_TZ{name_to_suffix(source_name)}"
    if tz_name is None:
        if environ_key in environ:
            del environ[environ_key]
    else:
        environ[environ_key] = tz_name


def _datetime_to_ts_insert(dt: Optional[datetime], force_utc: bool = True) -> str:
    # force_utc necessary if timezone of db has been switched to non-UTC
    # without it the db assumes the timestamp is specified in new tz
    return (
        "NULL"
        if dt is None
        else "'{0}{1}'".format(
            dt.strftime("%Y-%m-%d  %H:%M:%S.%f"), "+00" if force_utc else ""
        )
    )


def _datetime_to_date_insert(dt: Optional[datetime]) -> str:
    return (
        "NULL"
        if dt is None
        else "'{0}'".format(
            dt.strftime("%Y-%m-%d"),
        )
    )
