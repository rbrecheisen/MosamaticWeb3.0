@echo off
call shutdown-latest.bat
set /p PASSWORD=<C:\\Users\\r.brecheisen\\dockerhub.txt
docker logout
docker login --username brecheisen --password "%PASSWORD%"
docker push brecheisen/mosamatic3-nginx-amd64:latest
docker push brecheisen/mosamatic3-huey-amd64:latest
docker push brecheisen/mosamatic3-web-amd64:latest