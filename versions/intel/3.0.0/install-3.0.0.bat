@echo off
call shutdown-latest.bat
docker-compose -f docker-compose-3.0.0.yml build --no-cache
docker system prune -f