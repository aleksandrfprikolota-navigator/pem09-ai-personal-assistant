# PEm09. Помощник по «1С-Премиум»

Telegram-бот по компании «1С-Премиум»: мультимодальный ассистент с прямым подключением к OpenAI и базой знаний по сайту [1c-prem.ru](https://www.1c-prem.ru/about/).

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
