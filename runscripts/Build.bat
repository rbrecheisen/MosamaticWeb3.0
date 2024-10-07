@echo off
call runscripts\Shutdown.bat
set TAG=%1
docker-compose build --no-cache