FROM python:3.10-slim

WORKDIR /app

# system deps for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# install Python deps
COPY api_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy your app code
COPY api_service ./api_service
COPY common      ./common

# copy seed/start scripts
COPY api_service/scripts ./scripts

# satisfy `import interfaces.http.*`
RUN ln -s /app/api_service/interfaces /app/interfaces

# make sure scripts are executable
RUN chmod +x /app/scripts/start.sh

# Python module path
ENV PYTHONPATH=/app

EXPOSE 8000

# final entry point
CMD ["/app/scripts/start.sh"]
