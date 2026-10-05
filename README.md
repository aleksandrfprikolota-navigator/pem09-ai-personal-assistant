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

Подключение идёт напрямую в OpenAI. В `.env` нужны `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY`.

Ответ на задание: [PEm09 Ответ на задание.docx](PEm09%20Ответ%20на%20задание.docx). Бот: [@AI_MyPersonalAssistant_bot](https://t.me/AI_MyPersonalAssistant_bot). Репозиторий: [pem09-ai-personal-assistant](https://github.com/aleksandrfprikolota-navigator/pem09-ai-personal-assistant).
