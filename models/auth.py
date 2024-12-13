import uuid
import bcrypt
import jwt

class InvalidCredentialsError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class TokenExpiredError(Exception):
    pass

class InvalidTokenError(Exception):
    pass


def login_user(mysql, config, email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID, password FROM persons WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    if user and bcrypt.checkpw(password.encode(), user[1].encode()):
        token = jwt.encode({'id': user[0], 'email': email}, config.SECRET_KEY, algorithm="HS256")
        return {'message': 'Login successful', 'accessToken': token}
    raise InvalidCredentialsError("Invalid credentials")

def register_user(mysql, config, email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM persons WHERE email = %s", (email,))
    if cur.fetchone():
        raise UserAlreadyExistsError("User already exists")
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    cur.execute("INSERT INTO persons (ID, email, password) VALUES (%s, %s, %s)", (user_id, email, hashed_password))
    mysql.connection.commit()
    token = jwt.encode({'id': user_id, 'email': email}, config.SECRET_KEY, algorithm="HS256")
    return {'message': 'Registration successful', 'accessToken': token}

def authenticate_user(mysql, config, token):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (payload['id'],))
        user = cur.fetchone()
        cur.close()
        if user:
            return {'message': 'Authentication successful'}
        raise UserNotFoundError("User not found")
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")
