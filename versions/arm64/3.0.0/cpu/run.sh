#!/bin/bash

if [[ ! -f "shutdown.bat" ]]; then
    echo "Downloading shutdown.bat..."
    curl -o "shutdown.bat" "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/arm64/3.0.0/cpu/shutdown.bat"
    chmod +x ./shutdown.sh
fi

if [[ ! -f "docker-compose.yml" ]]; then
    echo "Downloading docker-compose.yml..."
    curl -o "shutdown.bat" "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/arm64/3.0.0/cpu/docker-compose.yml"
fi

./shutdown.sh
docker-compose up -d && docker-compose logs -f web huey