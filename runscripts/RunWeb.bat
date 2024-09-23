set POSTGRES_HOST=mosamatic3_postgres
docker-compose up -d %1 web && docker-compose logs -f web