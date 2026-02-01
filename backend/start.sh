#!/bin/bash
set -e

echo "========================================="
echo "Starting UNTANGLE Backend"
echo "========================================="

# Run migrations
echo "[1/3] Running database migrations..."
if alembic upgrade head; then
    echo "✓ Migrations completed successfully"
else
    echo "⚠ Migrations failed or already up to date"
fi

# Seed database (only if needed)
echo "[2/3] Seeding database..."
if python seed_data.py 2>/dev/null; then
    echo "✓ Database seeded successfully"
else
    echo "⚠ Seeding skipped (data may already exist)"
fi

# Start server
echo "[3/3] Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
