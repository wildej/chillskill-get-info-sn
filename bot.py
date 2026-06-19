"""
Телеграм бот для получения информации по серийному номеру.
"""
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from serial_number import parse_serial_number
from google_sheets import get_data_by_serial_number, format_data_for_display
from usage_log import log_usage

# Версия бота
BOT_VERSION = "0.0.4"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения!")

def _log_user_event(update: Update, event: str, serial: str = "", result: str = "") -> None:
    user = update.effective_user
    if user is None:
        return
    log_usage(
        user_id=user.id,
        username=user.username,
        event=event,
        serial=serial,
        result=result,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    Отправляет справку по использованию бота.
    """
    _log_user_event(update, event="start")
    help_text = (
        "👋 Добро пожаловать!\n\n"
        "Этот бот позволяет получить информацию по серийному номеру изделия.\n\n"
        "*Как пользоваться:*\n"
        "• Отправьте любой серийный номер (строкой) — бот найдёт информацию по нему в базе данных.\n"
        "• Если номер не соответствует формату или не найден — будет выведено сообщение об ошибке.\n\n"
        "/start — инструкция по работе с ботом\n\n"
        f"Версия бота: {BOT_VERSION}\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений.
    Обрабатывает серийный номер и ищет информацию в Google Sheets.
    """
    user_input = update.message.text.strip()
    
    # Парсим и валидируем серийный номер
    is_valid, result = parse_serial_number(user_input)
    
    if not is_valid:
        _log_user_event(update, event="lookup", result="validation_failed")
        await update.message.reply_text(f"❌ {result}")
        return
    
    # Серийный номер валиден и нормализован
    normalized_serial = result
    
    try:
        # Ищем данные в Google Sheets
        data = get_data_by_serial_number(normalized_serial)
        
        if data is None:
            _log_user_event(
                update,
                event="lookup",
                serial=normalized_serial,
                result="not_found",
            )
            await update.message.reply_text(
                f"❌ Серийный номер {normalized_serial} не найден в базе данных."
            )
        else:
            _log_user_event(
                update,
                event="lookup",
                serial=normalized_serial,
                result="found",
            )
            formatted_data = format_data_for_display(data)
            response = f"✅ *Серийный номер:* {normalized_serial}\n\n{formatted_data}"
            await update.message.reply_text(response, parse_mode="Markdown")
            
    except Exception as e:
        logger.exception("Ошибка при поиске данных для SN %s", normalized_serial)
        _log_user_event(
            update,
            event="lookup",
            serial=normalized_serial,
            result="error",
        )
        await update.message.reply_text(
            f"❌ Произошла ошибка при поиске данных: {str(e)}"
        )

def main() -> None:
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler(["start"], start_command))
    
    # Регистрируем обработчик текстовых сообщений (все сообщения, кроме команд)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен (версия %s)", BOT_VERSION)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
