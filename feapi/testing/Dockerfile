FROM feapi

RUN apk add --no-cache --update postgresql-client

COPY requirements-test.txt /requirements-test.txt
RUN pip install -r /requirements-test.txt

RUN mkdir -p /feapi/testing
COPY data /feapi/testing/data
COPY integration_tests /feapi/testing/integration_tests