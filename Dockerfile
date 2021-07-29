
FROM python:3.8-slim

RUN apt-get update && apt-get -y install python3-pip python3-psycopg2 libpq-dev
RUN rm -rf /var/lib/apt/lists/*

# OS dependencies required at runtime
RUN apt-get update && apt-get install -y curl

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm /requirements.txt

COPY ./feapi /feapi
RUN pip install -e /feapi/app


CMD ["gunicorn", "-c", "/feapi/fastapi/gunicorn/gunicorn.conf.py", "feapi.fastapi.api.main:app", "--timeout", "185"]
