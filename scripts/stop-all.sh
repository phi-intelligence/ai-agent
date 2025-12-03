#!/bin/bash

echo "Stopping Phi Agents Platform..."

# Read PIDs from file
if [ -f /tmp/phi-agents-pids.txt ]; then
    PIDS=$(cat /tmp/phi-agents-pids.txt)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping process $PID..."
            kill $PID
        fi
    done
    rm /tmp/phi-agents-pids.txt
fi

# Stop Docker containers
cd "$(dirname "$0")/../infra/docker"
docker-compose down

echo "✅ All services stopped"


