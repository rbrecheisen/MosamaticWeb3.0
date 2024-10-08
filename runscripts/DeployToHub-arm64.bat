@echo off
set /p PASSWORD=<C:\\Users\\r.brecheisen\\dockerhub.txt
docker logout
docker login --username brecheisen --password "%PASSWORD%"
docker push brecheisen/mosamatic3-nginx-arm64:latest
docker push brecheisen/mosamatic3-huey-arm64:latest
docker push brecheisen/mosamatic3-web-arm64:latest