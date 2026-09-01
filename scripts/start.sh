#!/bin/bash
# Start the SahaiSetu AI Triage System
set -e

cd "$(dirname "$0")/.."

echo "Starting SahaiSetu AI Triage System..."
docker compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Services:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Database:  localhost:5432"

echo ""
echo "To view logs: docker compose logs -f"
echo "To stop:      docker compose down"
