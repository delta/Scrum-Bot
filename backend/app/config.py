import logging
import os

from dotenv import dotenv_values

_dir_path = os.path.dirname(os.path.realpath(__file__))
_path = _dir_path + "/../.env"
config = dotenv_values(_path)

# general
FRONTEND_URL = config.get("FRONTEND_URL")
PROJECT_NAME = config.get("PROJECT_NAME", "Scrum_Bot")
DEBUG = config.get("DEBUG", "False") == "DEBUG"
PORT = int(config.get("PORT", 8000))
RELOAD = True if config.get("RELOAD", "1") == "1" else False

# database
MONGO_URI = config.get("MONGO_URI", "mongodb://127.0.0.1:27017/ScrumBot")

# jwt
JWT_ALGORITHM = config.get("JWT_ALGORITHM", "HS256")

JWT_SECRET = config.get("JWT_SECRET")

JWT_EXPIRE_TIME = int(config.get("JWT_EXPIRE_TIME", 0))


# Auth Headers
AUTH_HEADER_KEY = config.get("HEADER_KEY", "Authorization")

JWT_TOKEN_PREFIX = config.get("JWT_TOKEN_PREFIX", "Bearer")

# Bot Headers
BOT_HEADER_KEY = config.get("BOT_HEADER_KEY", "secure-bot-secret")
BOT_TOKEN_PREFIX = config.get("BOT_TOKEN_PREFIX")
BOT_SECRET_TOKEN = config.get("BOT_SECRET_TOKEN")

# logging
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
JSON_LOGS = True if config.get("JSON_LOGS", "0") == "1" else False

CONSTANTS = config.get("CONSTANTS").split("|")[:-1]
CONSTANTS_DEFAULT_VALUES = config.get("CONSTANTS_DEFAULT_VALUES").split("|")[:-1]
