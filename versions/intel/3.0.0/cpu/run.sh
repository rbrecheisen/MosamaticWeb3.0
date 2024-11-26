#!/bin/bash

if [ ! -e "shutdown.sh" ]; then
    echo "Downloading shutdown.sh..."
    curl -o "shutdown.sh" "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/3.0.0/cpu/shutdown.sh"
    chmod +x ./shutdown.sh
fi

if [ ! -e "docker-compose.yml" ]; then
    echo "Downloading docker-compose.yml..."
    curl -o "docker-compose.yml" "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/3.0.0/cpu/docker-compose-prod.yml"
fi

./shutdown.sh
docker-compose up -d && docker-compose logs -f web huey
