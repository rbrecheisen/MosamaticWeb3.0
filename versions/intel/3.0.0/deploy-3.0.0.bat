@echo off
call shutdown-3.0.0.bat
set /p PASSWORD=<C:\\Users\\r.brecheisen\\dockerhub.txt
docker logout
docker login --username brecheisen --password "%PASSWORD%"
docker push brecheisen/mosamatic3-nginx-amd64:3.0.0
docker push brecheisen/mosamatic3-huey-amd64:3.0.0
docker push brecheisen/mosamatic3-web-amd64:3.0.0