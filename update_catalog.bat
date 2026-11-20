@echo off
REM Run update_catalog.py from this script's directory (forwards any args).
cd /d "%~dp0"
python "%~dp0update_catalog.py" %*
exit /b %ERRORLEVEL%
