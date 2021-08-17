FROM oaff

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements-test.txt
RUN mkdir -p oaff/testing
COPY data oaff/testing/data
COPY integration_tests oaff/testing/integration_tests

