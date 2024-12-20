import os
from dotenv import load_dotenv
import logging

# Укажите путь к файлу .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEB_BASE_URL = os.getenv("WEB_BASE_URL")
    TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME")
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:5174", "https://surveity.vercel.app"]
    PORT = os.getenv("PORT")

logging.basicConfig(level=logging.DEBUG)
logging.debug(f"SECRET_KEY: {Config.SECRET_KEY}")
logging.debug(f"SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")
logging.debug(f"WEB_BASE_URL: {Config.WEB_BASE_URL}")
logging.debug(f"TELEGRAM_BOT_NAME: {Config.TELEGRAM_BOT_NAME}")
logging.debug(f"PORT: {Config.PORT}")
