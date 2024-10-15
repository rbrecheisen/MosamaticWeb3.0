runscripts/Shutdown.sh
docker-compose -f docker-compose-arm64-build.yml build --no-cache
docker system prune -f