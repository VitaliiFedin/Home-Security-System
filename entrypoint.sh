#!/bin/bash

# Function to wait for the database
wait_for_db() {
    echo "Waiting for database..."
    while ! nc -z db 5432; do
      sleep 0.1
    done
    echo "Database started"
}

# Wait for the database to be ready
wait_for_db

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the application
echo "Starting application..."
exec "$@"