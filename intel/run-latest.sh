#!/bin/bash
./shutdown-latest.sh
docker-compose up -d && docker-compose logs -f web huey