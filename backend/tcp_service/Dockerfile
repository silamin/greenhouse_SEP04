FROM python:3.10-slim

WORKDIR /app

# system deps for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# install Python deps
COPY tcp_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy your code *and* the shared api_service package
COPY tcp_service   ./tcp_service
COPY api_service   ./api_service
COPY common        ./common

ENV PYTHONPATH=/app

EXPOSE 9000

# run as a module so imports resolve under PYTHONPATH=/app
CMD ["python", "-m", "tcp_service.main"]
