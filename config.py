import os
from dotenv import load_dotenv

class Config:
    def __init__(self, env):
        self.env = env
        self.load_env()

    def load_env(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(base_dir, '.env.local' if self.env == 'development' else '.env.production')
        print(f"Loading environment variables from {env_file}")

        if not os.path.exists(env_file):
            print(f"Error: {env_file} does not exist")
            return

        load_dotenv(env_file)
        print("Environment variables loaded")

        self.MYSQL_HOST = os.getenv('MYSQL_HOST')
        self.MYSQL_USER = os.getenv('MYSQL_USER')
        self.MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
        self.MYSQL_DB = os.getenv('MYSQL_DB')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.PORT = int(os.getenv('PORT', 5000))
        self.CORS_ORIGINS = ["http://localhost:5173", "https://surveity.vercel.app"]
        self.FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL')

        print(f"MYSQL_HOST: {self.MYSQL_HOST}")
        print(f"MYSQL_USER: {self.MYSQL_USER}")
        print(f"MYSQL_PASSWORD: {self.MYSQL_PASSWORD}")
        print(f"MYSQL_DB: {self.MYSQL_DB}")
        print(f"SECRET_KEY: {self.SECRET_KEY}")
        print(f"PORT: {self.PORT}")
        print(f"FRONTEND_URL: {self.FRONTEND_BASE_URL}")

