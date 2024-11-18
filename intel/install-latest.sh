#!/bin/bash
./shutdown-latest.sh
docker-compose build --no-cache
docker system prune -f