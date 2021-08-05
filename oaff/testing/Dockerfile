FROM oaff

RUN apk add --no-cache --update postgresql-client

COPY requirements-test.txt /requirements-test.txt
RUN pip install -r /requirements-test.txt

RUN mkdir -p /oaff/testing
COPY data /oaff/testing/data
COPY integration_tests /oaff/testing/integration_tests