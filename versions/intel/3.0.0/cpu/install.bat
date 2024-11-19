@echo off
call shutdown.bat
docker-compose build --no-cache
docker system prune -f