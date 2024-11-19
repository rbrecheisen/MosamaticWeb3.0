#!/bin/bash
./shutdown.sh
export PASSWORD=$(cat $HOME/dockerhubpassword.txt)
docker logout
docker login --username brecheisen --password "${PASSWORD}"
docker push brecheisen/mosamatic3-nginx-intel-gpu:latest
docker push brecheisen/mosamatic3-huey-intel-gpu:latest
docker push brecheisen/mosamatic3-web-intel-gpu:latest