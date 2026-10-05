"""
Image Handler.
Handles image analysis with GPT-4 Vision using pyTelegramBotAPI.
"""

from telebot import types
from bot import bot
from services.router import route_image_request
from handlers.document_upload import process_document_upload
from utils.logging import logger
from utils.helpers import cleanup_file


@bot.message_handler(content_types=['photo'])
async def handle_photo_message(message: types.Message):
    """Handle photo messages."""
    user_id = message.from_user.id
    
    logger.info(f"Photo message from user {user_id}")
    
    # Show typing indicator
    await bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Get the largest photo
        photo = message.photo[-1]
        
        # Get caption if provided
        caption = message.caption
        
        # Get file URL (for Vision API)
        file_info = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        logger.debug(f"Image URL: {file_url}")
        
        # Notify user
        if caption:
            await bot.send_message(
                message.chat.id,
                f"📸 Анализирую изображение с вопросом:\n_{caption}_"
            )
        else:
            await bot.send_message(message.chat.id, "📸 Анализирую изображение...")
        
        # Process image request
        response = await route_image_request(
            user_id=user_id,
            image_url=file_url,
            caption=caption
        )
        
        # Send analysis result
        await bot.send_message(
            message.chat.id,
            f"🔍 **Анализ изображения:**\n\n{response['text']}"
        )
    
    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        await bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при анализе изображения.\n"
            "Попробуйте отправить другое изображение."
        )


@bot.message_handler(content_types=['document'])
async def handle_document_message(message: types.Message):
    """Handle document messages (could be PDFs for RAG)."""
    user_id = message.from_user.id
    document = message.document
    
    file_name = (document.file_name or "").lower()
    supported = (
        document.mime_type in {"application/pdf", "text/plain", "text/markdown"}
        or file_name.endswith((".pdf", ".txt", ".md"))
    )

    if supported:
        await process_document_upload(message, document)
    elif document.mime_type and document.mime_type.startswith("image/"):
        # Handle as image
        await bot.send_message(
            message.chat.id,
            "📸 Получено изображение в виде документа.\n"
            "Отправьте изображение как фото для анализа."
        )
    else:
        await bot.send_message(
            message.chat.id,
            f"ℹ️ Получен файл: {document.file_name}\n"
            f"Тип: {document.mime_type}\n\n"
            "Поддерживаемые файлы для базы знаний:\n"
            "• PDF, TXT и Markdown\n"
            "• Изображения отправляйте как фото"
        )
