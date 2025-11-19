#!/bin/bash

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready at host: $DB_HOST, port: $DB_PORT..."

    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
        sleep 2
    done

    echo "✅ PostgreSQL is ready!"
}

# Set default DB env values if not passed
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}

# Wait for PostgreSQL to be ready
wait_for_postgres

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY environment variable is not set"
    echo "   Make sure to set it in your environment or docker-compose.yml"
fi

# Start FastAPI application
echo "🚀 Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload