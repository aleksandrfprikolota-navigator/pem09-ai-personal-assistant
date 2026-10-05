@echo off
cd /d "%~dp0"
if not exist .env (
    echo Создайте файл .env на основе .env.example и укажите TELEGRAM_BOT_TOKEN и OPENAI_API_KEY.
    exit /b 1
)
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe main.py
) else (
    python main.py
)
