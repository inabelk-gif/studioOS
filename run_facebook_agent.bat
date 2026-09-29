@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ==== %date% %time% >> "data\facebook_agent.log"
"C:\Python314\python.exe" facebook_agent.py >> "data\facebook_agent.log" 2>&1
