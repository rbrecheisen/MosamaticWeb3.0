@echo off
setlocal enabledelayedexpansion

@rem Check if shutdown.bat available. If so, call it
if exist "shutdown-3.0.0.bat" (
    call shutdown-3.0.0.bat
)

@rem Check if docker-compose.yml available. If not, download it
if not exist "docker-compose-3.0.0.yml" (
    set "COMPOSE_FILE_URL=https://raw.githubusercontent.com/your-repo/your-project/main/docker-compose.yml"
    powershell -Command "Invoke-WebRequest -Uri %COMPOSE_FILE_URL% -OutFile 'docker-compose-3.0.0.yml'"
)

@rem Run application
docker-compose -f docker-compose-3.0.0.yml up -d && docker-compose logs -f web huey