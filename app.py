# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import logging
from routes import register_routes
import git
from config import Config
from utils.db import create_tables


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение окружения
env = os.getenv('FLASK_ENV', 'production')
config = Config(env)

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['PORT'] = config.PORT

CORS(app, origins=config.CORS_ORIGINS,
     supports_credentials=True,
     allow_headers=["Authorization", "Content-Type"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

mysql = MySQL(app)


# Создание таблиц
create_tables(app, mysql)

register_routes(app, mysql, logger, config)

@app.route('/update_server', methods=['POST'])
def update_server():
    try:
        repo = git.Repo('/home/surveity/production')
        origin = repo.remotes.origin
        origin.pull()
        logger.info('Server updated successfully')
        return 'Server updated successfully', 200
    except Exception as e:
        logger.error(f'Error during the update: {e}')
        return jsonify({'error': 'Error during the update', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=(env == 'development'), port=config.PORT, host='0.0.0.0')
