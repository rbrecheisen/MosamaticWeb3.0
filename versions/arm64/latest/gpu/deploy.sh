#!/bin/bash
export PASSWORD=$(cat $HOME/dockerhubpassword.txt)
docker logout
docker login --username brecheisen --password "${PASSWORD}"
docker push brecheisen/mosamatic3-nginx-arm64-gpu:latest
docker push brecheisen/mosamatic3-huey-arm64-gpu:latest
docker push brecheisen/mosamatic3-web-arm64-gpu:latest