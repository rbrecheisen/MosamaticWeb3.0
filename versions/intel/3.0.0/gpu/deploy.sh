#!/bin/bash
export PASSWORD=$(cat $HOME/dockerhubpassword.txt)
docker logout
docker login --username brecheisen --password "${PASSWORD}"
docker push brecheisen/mosamatic3-nginx-intel-gpu:3.0.0
docker push brecheisen/mosamatic3-huey-intel-gpu:3.0.0
docker push brecheisen/mosamatic3-web-intel-gpu:3.0.0
