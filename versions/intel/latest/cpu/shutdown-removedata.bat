docker-compose down --volumes --remove-orphans
docker container prune -f
docker volume prune -f
docker system prune -f