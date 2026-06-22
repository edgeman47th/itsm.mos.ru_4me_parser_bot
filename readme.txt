# itsm.mos.ru_4me_parser_bot

Бот для уведомлений о новых заявках из 4me (Inbox) в Telegram.

## Установка на Ubuntu 24.04

```bash
sudo apt update && sudo apt install python3 python3-venv git -y

cd /opt
sudo git clone https://github.com/edgeman47th/itsm.mos.ru_4me_parser_bot.git
sudo chown -R $USER:$USER itsm.mos.ru_4me_parser_bot
cd itsm.mos.ru_4me_parser_bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env
