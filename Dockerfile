
FROM python:3.8-slim-bullseye

RUN apt-get update && apt-get install -y \
      # OS dependencies only required to build certain Python dependencies
      libpq-dev \
      python3-pip \
      python3-psycopg2 \
      # OS dependency required at runtime
      curl \ 
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ogc-api-fast-features
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY oaff oaff
RUN pip install -e oaff/app


CMD ["gunicorn", "-c", "/opt/ogc-api-fast-features/oaff/fastapi/gunicorn/gunicorn.conf.py", "oaff.fastapi.api.main:app", "--timeout", "185"]
