from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Настройка CORS
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         allow_headers=["Authorization", "Content-Type", "Access-Control-Allow-Origin"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)  # Убедитесь, что это включено

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes import auth_routes, tests_routes, questions_routes, answers_routes, sessions_routes
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(tests_routes.bp)
    app.register_blueprint(sessions_routes.bp)
    app.register_blueprint(questions_routes.bp)
    app.register_blueprint(answers_routes.bp)

    return app
