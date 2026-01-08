"""
Телеграм бот для получения информации по серийному номеру.
"""
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from serial_number import parse_serial_number
from google_sheets import get_data_by_serial_number, format_data_for_display

# Версия бота
BOT_VERSION = "0.0.1"

# Загружаем переменные окружения
load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения!")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    Отправляет справку по использованию бота.
    """
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
        # Если валидация не прошла, отправляем сообщение об ошибке
        await update.message.reply_text(f"❌ {result}")
        return
    
    # Серийный номер валиден и нормализован
    normalized_serial = result
    
    try:
        # Ищем данные в Google Sheets
        data = get_data_by_serial_number(normalized_serial)
        
        if data is None:
            await update.message.reply_text(
                f"❌ Серийный номер {normalized_serial} не найден в базе данных."
            )
        else:
            # Форматируем и отправляем данные
            formatted_data = format_data_for_display(data)
            response = f"✅ *Серийный номер:* {normalized_serial}\n\n{formatted_data}"
            await update.message.reply_text(response, parse_mode="Markdown")
            
    except Exception as e:
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
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
