FROM feapi

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client-11 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/$NAME
COPY requirements-test.txt requirements-test.txt
RUN pip install -r requirements-test.txt --no-cache-dir 

WORKDIR /
RUN mkdir -p /feapi/testing
COPY data /feapi/testing/data
COPY integration_tests /feapi/testing/integration_tests