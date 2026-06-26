# itsm.mos.ru_4me_parser_bot
Бот для уведомлений о **новых заявках в Inbox** системы ИТСМ (ПУДС / 4me).
Бот периодически проверяет входящие заявки и отправляет красивые уведомления в Telegram.
## Возможности
- Уведомления о новых заявках в Inbox
- Поддержка подписки/отписки (`/subscribe`, `/unsubscribe`)
- Красивый HTML-шаблон сообщений
- Сохранение состояния (не спамит старыми заявками)
- Запуск через Docker (рекомендуется)
## Установка на чистую Ubuntu 24.04
### Шаг 1: Обновление системы и установка Docker
```BASH
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ca-certificates

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```
### Шаг 2: Клонирование репозитория
```BASH
cd /opt
sudo mkdir -p itsm.mos.ru_4me_parser_bot
sudo chown $USER:$USER itsm.mos.ru_4me_parser_bot
cd itsm.mos.ru_4me_parser_bot

git clone https://github.com/edgeman47th/itsm.mos.ru_4me_parser_bot.git .
```
### Шаг 3: Настройка конфигурации
```BASH
cp .env.example .env
nano .env
```
#### Заполните файл следующими данными:
###### Telegram
TELEGRAM_BOT_TOKEN=
###### 4me / ИТСМ
4ME_BEARER_TOKEN=твой_полный_bearer_token
4ME_ACCOUNT_ID=sc-tech-solutions

### Шаг 4: Запуск бота
```BASH
# Первый запуск (сборка)
docker compose up -d --build

# Просмотр логов
docker compose logs -f
```
### Полезные команды
#### Перезапуск бота
docker compose restart
#### Пересборка после изменений кода
docker compose up -d --build
#### Остановить бота
docker compose down
#### Просмотр логов за последние 100 строк
docker compose logs --tail=100
#### Статус контейнера
docker compose ps