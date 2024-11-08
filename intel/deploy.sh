#!/bin/bash
./shutdown.sh
export PASSWORD=$(cat $HOME/dockerhubpassword.txt)
docker logout
docker login --username brecheisen --password "${PASSWORD}"
docker push brecheisen/mosamatic3-nginx-amd64:latest
docker push brecheisen/mosamatic3-huey-amd64:latest
docker push brecheisen/mosamatic3-web-amd64:latest