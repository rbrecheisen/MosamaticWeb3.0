@echo off
call shutdown-latest.bat
docker-compose build --no-cache
docker system prune -f