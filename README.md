# Телеграм бот для генерации и проверки серийных номеров

Бот для получения информации о продукте по его серийному номеру. Информация хранится в таблице Google Sheet.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example` и укажите токен вашего бота:
```
BOT_TOKEN=your_bot_token_here
```

## Запуск

### Локальный запуск

```bash
python bot.py
```

### Запуск в Docker

#### Использование Docker Compose (рекомендуется)

1. Убедитесь, что файл `.env` создан и содержит токен бота
2. Запустите контейнер:
```bash
docker-compose up -d
```

3. Просмотр логов:
```bash
docker-compose logs -f
```

4. Остановка контейнера:
```bash
docker-compose down
```

#### Использование Docker напрямую

1. Соберите образ:
```bash
docker build -t telegram-chillskill-info-bot .
```

2. Запустите контейнер:
```bash
docker run -d --name telegram-chillskill-info-bot --env-file .env --restart unless-stopped telegram-chillskill-info-bot
```

3. Просмотр логов:
```bash
docker logs -f telegram-chillskill-info-bot
```

4. Остановка контейнера:
```bash
docker stop telegram-chillskill-info-bot
docker rm telegram-chillskill-info-bot
```

## Команды бота

## Примеры использования

```
```
