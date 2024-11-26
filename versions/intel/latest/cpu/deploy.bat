@echo off
call shutdown.bat
set /p PASSWORD=<C:\\Users\\r.brecheisen\\dockerhub.txt
docker logout
docker login --username brecheisen --password "%PASSWORD%"
docker push brecheisen/mosamatic3-nginx-intel-cpu:latest
docker push brecheisen/mosamatic3-huey-intel-cpu:latest
docker push brecheisen/mosamatic3-web-intel-cpu:latest