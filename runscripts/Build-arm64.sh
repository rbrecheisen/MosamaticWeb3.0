runscripts/Shutdown.sh
# docker buildx create --name arm64builder --use
docker-compose -f docker-compose-arm64-build.yml build --no-cache
# docker buildx rm arm64builder