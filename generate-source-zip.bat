@echo off
set ZIP_NAME="C:\Users\r.brecheisen\Desktop\MosamaticWeb3.0-source.zip"
set FILE_LIST=sources.txt
PowerShell -Command "Compress-Archive -Path (Get-Content %FILE_LIST%) -DestinationPath %ZIP_NAME% -Force"
pause