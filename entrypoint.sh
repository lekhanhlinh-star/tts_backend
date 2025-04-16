#!/usr/bin/env sh
# Wait for the database to be ready



set -e

echo "🟢 Starting Celery worker..."
celery -A app.background.tasks worker --loglevel=info --concurrency=1 --pool=solo &

sleep 15  # Increase sleep time here

echo "🟢 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port=8080
