# PEm09. Личный помощник

Учебный Telegram-бот модуля: мультимодальный ассистент с прямым подключением к OpenAI и базой знаний RAG.

Код и инструкция по запуску: [Project_AI_MPA/README.md](Project_AI_MPA/README.md).

```bash
cd Project_AI_MPA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

ProxyAPI в проекте нет. В `.env` нужны только `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY`.
