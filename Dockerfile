
FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
      # OS dependencies only required to build certain Python dependencies
      libpq-dev \
      python3-pip \
      python3-psycopg2 \
      # OS dependency required at runtime
      curl \ 
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/$NAME
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN rm requirements.txt

WORKDIR /
COPY ./feapi /feapi
RUN pip install -e /feapi/app


CMD ["gunicorn", "-c", "/feapi/fastapi/gunicorn/gunicorn.conf.py", "feapi.fastapi.api.main:app", "--timeout", "185"]
