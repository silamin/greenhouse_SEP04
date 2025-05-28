#!/bin/sh

# Start the FastAPI app in the background
uvicorn api_service.main:app --host 0.0.0.0 --port 8000 &

# Wait a bit for the DB to be ready (adjust if needed)
echo "Waiting for DB to initialize..."
sleep 5

# Seed the database
echo "Running seed script..."
python /app/scripts/seed.py

# Keep the container running
wait
