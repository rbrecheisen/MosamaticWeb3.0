#!/bin/bash
./shutdown.sh
export PASSWORD=$(cat $HOME/dockerhubpassword.txt)
docker logout
docker login --username brecheisen --password "${PASSWORD}"
docker push brecheisen/mosamatic3-nginx-intel-cpu:latest
docker push brecheisen/mosamatic3-huey-intel-cpu:latest
docker push brecheisen/mosamatic3-web-intel-cpu:latest