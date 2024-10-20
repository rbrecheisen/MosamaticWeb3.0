@echo off
call runscripts\Shutdown.bat
docker-compose -f docker-compose-build.yml build --no-cache
docker system prune -f