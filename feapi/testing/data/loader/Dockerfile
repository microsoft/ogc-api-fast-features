FROM python:3.9.5-alpine3.13

RUN apk add --no-cache --update \
  bash \
  postgresql-client

RUN apk add --no-cache --update --virtual .build-deps gcc libc-dev make python3-dev postgresql-dev \
  && pip install psycopg2-binary==2.8.6 \
  && apk del .build-deps

COPY sql /sql
COPY load /load

CMD [ "/load/setup.sh" ]