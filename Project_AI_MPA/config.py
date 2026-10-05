"""
Configuration module for the Personal Assistant Telegram Bot.
Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# OpenAI Configuration. Подключение только к официальному API, без ProxyAPI.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1"


def validate_config() -> None:
    """Проверяет обязательные ключи. Вызывается при запуске бота."""
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        raise ValueError(
            "Не заданы переменные окружения: "
            + ", ".join(missing)
            + ". Скопируйте .env.example в .env и укажите ключи."
        )

# Bot Modes
class BotMode:
    TEXT = "text"
    VOICE = "voice"
    VISION = "vision"
    RAG = "rag"

DEFAULT_MODE = os.getenv("BOT_MODE", BotMode.TEXT)

# Voice Configuration
class VoiceType:
    ALLOY = "alloy"      # Neutral
    ECHO = "echo"        # Male
    NOVA = "nova"        # Female
    FABLE = "fable"      # Male (British)
    ONYX = "onyx"        # Male (Deep)
    SHIMMER = "shimmer"  # Female (Warm)

DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", VoiceType.ALLOY)

# OpenAI Models
GPT_MODEL = "gpt-4o"
GPT_MINI_MODEL = "gpt-4o-mini"
WHISPER_MODEL = "whisper-1"
TTS_MODEL = "tts-1"
VISION_MODEL = "gpt-4o"
DALLE_MODEL = "dall-e-3"

# DALL-E Configuration
DALLE_DEFAULT_SIZE = "1024x1024"  # Options: 1024x1024, 1024x1792, 1792x1024
DALLE_DEFAULT_QUALITY = "standard"  # Options: standard, hd
DALLE_DEFAULT_STYLE = "vivid"  # Options: vivid, natural

# Database Configuration
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/embeddings.db")

# Data paths
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
EMBEDDINGS_DB = DATA_DIR / "embeddings.db"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "bot.log"

# RAG Configuration
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_TOP_K = 3

# OpenAI Settings
TEMPERATURE = 0.7
MAX_TOKENS = 1500

# User session settings
MAX_HISTORY_LENGTH = 10  # Maximum number of messages to keep in history

# Роль ассистента: личный учебный помощник студента курса по ИИ.
TEXT_SYSTEM_PROMPT = """Ты — личный учебный ассистент студента курса по искусственному интеллекту.
Помогаешь разбирать теорию ИИ и Python, готовиться к практике и помнить контекст текущего диалога.
Отвечай по-русски, ясно и по делу.
Если пользователь ссылается на прошлые реплики, опирайся на историю переписки.
Не выдумывай контакты курса, дедлайны и состав базы знаний: эти факты есть только в режиме RAG.
Если вопрос похож на запрос к учебным материалам, предложи команду /mode rag."""

RAG_SYSTEM_PROMPT = """Ты — личный учебный ассистент. Отвечай только по фрагментам базы знаний.

ПРАВИЛА:
1. Используй предоставленный контекст как единственный источник фактов.
2. Если в контексте есть ответ, сформулируй его своими словами и укажи имя файла-источника.
3. Если контекста недостаточно, прямо скажи, что в базе знаний этого нет. Не додумывай факты.
4. Учитывай недавнюю историю диалога, чтобы понимать уточняющие вопросы.
5. Пиши по-русски, коротко и структурированно.

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}"""

