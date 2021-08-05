/*
  This query returns all geospatial tables within the database that may be exposed as layers.
  It excludes tables with multiple geometry columns and tables with composite primary keys.
  All tables must have a non-null SRID
*/
WITH geom_geog_columns AS (
  SELECT f_table_schema schema_name
       , f_table_name table_name
       , f_geometry_column geometry_field
       , srid
    FROM geometry_columns
   UNION
  SELECT f_table_schema schema_name
       , f_table_name table_name
       , f_geography_column geometry_field
       , srid
    FROM geography_columns
), single_geom_tables AS (
   SELECT gc.schema_name
        , gc.table_name
        , gc.geometry_field
        , srs.srid srid
        , srs.auth_name
        , srs.auth_srid auth_code 
     FROM geom_geog_columns gc
     JOIN (
       SELECT schema_name
            , table_name
         FROM geom_geog_columns
     GROUP BY schema_name
            , table_name
       HAVING COUNT(*) = 1
     ) s ON gc.schema_name = s.schema_name AND gc.table_name = s.table_name
LEFT JOIN spatial_ref_sys srs ON gc.srid = srs.srid
), single_pk_tables AS (
  SELECT kcu.table_schema schema_name
       , kcu.table_name
       , kcu.column_name unique_field
    FROM information_schema.key_column_usage kcu
    JOIN (
    SELECT kcu.constraint_name
         , COUNT(*)
      FROM information_schema.key_column_usage kcu
      JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name AND tc.constraint_type = 'PRIMARY KEY'
  GROUP BY kcu.constraint_name
    HAVING COUNT(*) = 1
         ) spk ON kcu.constraint_name = spk.constraint_name
       order by kcu.table_schema
       , kcu.table_name
       , kcu.column_name
), eligible_tables AS (
  SELECT schemaname schema_name
       , tablename table_name
    FROM pg_catalog.pg_tables
   WHERE schemaname NOT IN('pg_catalog', 'information_schema', 'oaff')
)
   SELECT QUOTE_IDENT(et.schema_name) || '.' || QUOTE_IDENT(et.table_name) qualified_table_name
        , et.schema_name
        , et.table_name
        , CASE
            WHEN sgt.table_name IS NULL THEN 'exactly one spatial column required'
            WHEN sgt.srid IS NULL THEN 'non-null SRID is required'
            WHEN spt.table_name IS NULL THEN 'exactly one primary key column required'
            ELSE NULL
          END exclude_reason
        , sgt.geometry_field
        , sgt.srid
        , sgt.auth_name
        , sgt.auth_code
     FROM eligible_tables et
LEFT JOIN single_geom_tables sgt ON et.schema_name = sgt.schema_name AND et.table_name = sgt.table_name
LEFT JOIN single_pk_tables spt ON et.schema_name = spt.schema_name AND et.table_name = spt.table_name
;