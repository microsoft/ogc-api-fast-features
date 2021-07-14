#!/bin/bash

iteration=0
until python -m load.db_check || [ "$iteration" -gt "30" ]
do
  ((iteration++))
  echo "Waiting on db connection, iteration $iteration"
  sleep 1
done

PGPASSWORD=$APP_POSTGRESQL_PASSWORD psql -h $APP_POSTGRESQL_HOST -U $APP_POSTGRESQL_USER -f /sql/all.sql