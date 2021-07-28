
FROM osgeo/gdal:alpine-normal-3.3.0

COPY requirements_build.txt /requirements_build.txt
RUN apk add --no-cache --update py3-pip py3-psycopg2
# OS dependencies only required to build certain Python dependencies
RUN apk add --no-cache --update --virtual .build-deps gcc libc-dev make python3-dev \
  && pip install -r /requirements_build.txt \
  && apk del .build-deps
RUN rm /requirements_build.txt
# OS dependencies required at runtime
RUN apk add --no-cache --update \
  bash \
  curl

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm /requirements.txt

COPY ./feapi /feapi
RUN pip install -e /feapi/app


CMD ["gunicorn", "-c", "/feapi/fastapi/gunicorn/gunicorn.conf.py", "feapi.fastapi.api.main:app", "--timeout", "185"]
