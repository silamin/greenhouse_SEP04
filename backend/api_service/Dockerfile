FROM python:3.10-slim

WORKDIR /app

# install curl for HEALTHCHECK
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy your application code
COPY . ./

EXPOSE 80

# Healthcheck against your /health endpoint
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=10s \
            --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# start your FastAPI app (adjust module:path as needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
