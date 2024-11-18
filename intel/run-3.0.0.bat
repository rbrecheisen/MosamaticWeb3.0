@echo off
setlocal enabledelayedexpansion

@rem Check if shutdown.bat available. If so, call it
if exist "shutdown-3.0.0.bat" (
    call shutdown-3.0.0.bat
)

@rem Check if docker-compose.yml available. If not, download it
if not exist "docker-compose-3.0.0.yml" (
    echo "Downloading docker-compose.yml..."
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rbrecheisen/MosamaticWeb3.0/refs/heads/main/intel/docker-compose-3.0.0.yml?token=GHSAT0AAAAAACXVUKOOL7RATQ7XBG7S7UB4ZZ3H7LA' -OutFile 'docker-compose-3.0.0.yml'"
)

@rem Run application
docker-compose -f docker-compose-3.0.0.yml up -d 
docker-compose -f docker-compose-3.0.0.yml logs -f web huey