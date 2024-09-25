call runscripts\Build.bat --no-cache
docker-compose up -d %1 && docker-compose logs -f