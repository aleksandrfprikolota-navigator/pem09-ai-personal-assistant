"""
Main Bot Module.
Initializes and configures the Telegram bot using pyTelegramBotAPI.
"""

from telebot.async_telebot import AsyncTeleBot

from config import TELEGRAM_BOT_TOKEN
from utils.logging import logger


# Пустой токен не проходит проверку pyTelegramBotAPI. Настоящая проверка ключей — в main.py.
_token = TELEGRAM_BOT_TOKEN or "0:missing"
bot = AsyncTeleBot(_token, parse_mode='Markdown')

_send_message = bot.send_message


async def _send_message_safe(chat_id, text, **kwargs):
    """Повторяет отправку без Markdown, если ответ модели сломал разметку Telegram."""
    try:
        return await _send_message(chat_id, text, **kwargs)
    except Exception as exc:
        error_text = str(exc).lower()
        if "parse" not in error_text and "can't find end" not in error_text:
            raise
        logger.warning(f"Markdown parse failed, sending plain text: {exc}")
        plain_kwargs = dict(kwargs)
        plain_kwargs["parse_mode"] = None
        return await _send_message(chat_id, text, **plain_kwargs)


bot.send_message = _send_message_safe

logger.info("Bot instance created")
