FROM feapi

RUN apt-get update && apt-get install -y postgresql-client-11
RUN rm -rf /var/lib/apt/lists/*

COPY requirements-test.txt /requirements-test.txt
RUN pip install -r /requirements-test.txt

RUN mkdir -p /feapi/testing
COPY data /feapi/testing/data
COPY integration_tests /feapi/testing/integration_tests