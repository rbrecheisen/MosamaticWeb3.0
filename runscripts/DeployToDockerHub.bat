@echo off
set /p TAG=<TAG.txt
set /p CONFIRM="Is the current tag %TAG% correct (y/n)?"
set /p PASSWORD=<C:\\Users\\r.brecheisen\\dockerhub.txt
if "%CONFIRM%" == "y" (
    docker logout
    docker login --username brecheisen --password "%PASSWORD%"
    docker push brecheisen/mosamatic3-nginx-amd64:%TAG%
    docker push brecheisen/mosamatic3-huey-amd64:%TAG%
    docker push brecheisen/mosamatic3-web-amd64:%TAG%
)