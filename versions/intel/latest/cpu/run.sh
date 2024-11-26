#!/bin/bash

if [ ! -e "shutdown.sh" ]; then
    echo "Downloading shutdown.sh..."
    curl -O "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/latest/cpu/shutdown.sh"
fi

if [ ! -e "docker-compose.yml" ]; then
    echo "Downloading docker-compose.yml..."
    curl -O "https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/latest/cpu/docker-compose-prod.yml"
fi

./shutdown.sh
docker-compose up -d && docker-compose logs -f web huey
