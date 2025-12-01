#!/bin/bash
#
# Run the IoT device simulator
#
# Usage:
#   ./run_simulator.sh              # Run with defaults (60s interval)
#   ./run_simulator.sh --interval 10 # Run with 10s interval
#   ./run_simulator.sh --once       # Send data once and exit
#   ./run_simulator.sh --approve    # Auto-approve devices in database
#   ./run_simulator.sh --approve --db-url "postgresql://user:pass@host:5432/db"
#
# Docker usage:
#   docker compose --profile simulator up -d simulator
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Docker not available, trying local Python..."

# Check if requests is installed, install if not
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests..."
    pip3 install --break-system-packages requests 2>/dev/null || pip3 install --user requests
}

# Check if psycopg2 is installed (needed for --approve)
python3 -c "import psycopg2" 2>/dev/null || {
    echo "Installing psycopg2-binary..."
    pip3 install --break-system-packages psycopg2-binary 2>/dev/null || pip3 install --user psycopg2-binary
}

# Run the simulator
python3 "$SCRIPT_DIR/simulate_devices.py" "$@"
