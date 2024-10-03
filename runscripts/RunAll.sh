runscripts/Build.sh
docker-compose up -d $1 && docker-compose logs -f web huey