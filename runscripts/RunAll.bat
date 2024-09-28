call runscripts\Shutdown.bat
docker-compose up -d %1 && docker-compose logs -f web huey nginx