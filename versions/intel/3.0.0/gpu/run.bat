@echo off
setlocal enabledelayedexpansion

@rem Check if shutdown.bat available. If so, call it
if not exist "shutdown.bat" (
    echo "Downloading shutdown.bat..."
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/3.0.0/gpu/shutdown.bat' -OutFile 'shutdown.bat'"
)

@rem Check if docker-compose.yml available. If not, download it
if not exist "docker-compose.yml" (
    echo "Downloading docker-compose.yml..."
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/versions/intel/3.0.0/gpu/docker-compose-prod.yml' -OutFile 'docker-compose.yml'"
)

@rem Run application
call shutdown.bat
docker-compose up -d 
docker-compose logs -f web huey