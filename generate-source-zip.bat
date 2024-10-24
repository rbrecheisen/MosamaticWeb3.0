@echo off

for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set GIT_COMMIT_ID=%%i
set ZIP_NAME="C:\Users\r.brecheisen\Desktop\MosamaticWeb3.0-source-%GIT_COMMIT_ID%.zip"
set FILE_LIST=sources.txt
PowerShell -Command "Compress-Archive -Path (Get-Content %FILE_LIST%) -DestinationPath %ZIP_NAME% -Force"
pause