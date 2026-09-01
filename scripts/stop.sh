#!/bin/bash
# Stop the SahaiSetu AI Triage System
set -e

cd "$(dirname "$0")/.."

echo "Stopping SahaiSetu AI Triage System..."
docker compose down
echo "Done."
