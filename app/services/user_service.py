from datetime import timedelta

from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

class UserService:
    @staticmethod
    def create_user(data):
        new_user = User(email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def check_password(user, password):
        return user.check_password(password)

    @staticmethod
    def create_access_token(user):
        additional_claims = {"email": user.email}
        expires_delta = timedelta(hours=24)
        return create_access_token(identity=str(user.id), additional_claims=additional_claims, expires_delta=expires_delta)
