@echo off
rem Set tag version in docker-compose.yml
set /p TAG=<TAG.txt
set /p CONFIRM="Current tag is %TAG%. Is this correct? (y/n)"
if "%CONFIRM%" == "y" (
    call runscripts\Shutdown.bat
    docker-compose build --no-cache
    rem Set this tag as latest tag
    docker tag brecheisen/mosamatic3-nginx-amd64:%TAG% brecheisen/mosamatic3-nginx-amd64:latest
    docker tag brecheisen/mosamatic3-web-amd64:%TAG% brecheisen/mosamatic3-web-amd64:latest
    docker tag brecheisen/mosamatic3-huey-amd64:%TAG% brecheisen/mosamatic3-huey-amd64:latest
)