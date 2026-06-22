from configparser import ConfigParser

config = ConfigParser()
config.read('./config.ini')

BOT_TOKEN = config["Telegram"]["bot_token"]
BEARER_TOKEN = config["AUTH"]["BEARER_TOKEN"]
ACCOUNT_ID = config["AUTH"]["ACCOUNT_ID"]