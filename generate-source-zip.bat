@echo off

for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set GIT_COMMIT_ID=%%i
set ZIP_NAME="C:\Users\r.brecheisen\Desktop\MosamaticWeb3.0-source-%GIT_COMMIT_ID%.zip"
set FILE_LIST=sources.txt
@REM PowerShell -Command "Compress-Archive -Path (Get-Content %FILE_LIST%) -DestinationPath %ZIP_NAME% -Force"
@REM PowerShell -NoProfile -ExecutionPolicy Bypass -Command ^
@REM     "foreach ($item in Get-Content '%TEMP_FILE%') { Compress-Archive -Path $item.Trim() -DestinationPath '%ZIP_NAME%' -Update }"

for %%F in ("%FILE_LIST%") do (
    if /I "%%~xF"==".sh" (
        powershell -Command "(Get-Content %%F) | Set-Content -NoNewline -Encoding ASCII %%F"
    )
)

PowerShell -NoProfile -ExecutionPolicy Bypass -Command ^
    "foreach ($item in Get-Content '%FILE_LIST%' -Raw -Delimiter `n) { Compress-Archive -Path $item.Trim() -DestinationPath '%ZIP_NAME%' -Update }"
    
pause