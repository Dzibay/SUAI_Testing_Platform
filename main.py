from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from flask_cors import CORS
import bcrypt
import uuid
import jwt


app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])


app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "database"
app.config['SECRET_KEY'] = 'SECRET_KEY'

mysql = MySQL(app)


def get_jwt_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None


@app.route("/api/v1/auth/authentication", methods=['POST'])
def authentication():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload['payloads']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (user_id,))
        if cur.fetchone():
            return make_response(jsonify({'message': 'Authenticated'}), 200)
        else:
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)


@app.route("/api/v1/auth/login", methods=['POST'])
def login():
    try:
        email, password = request.json['email'], request.json['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT ID, password FROM persons WHERE email = %s", (email,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode(), user[1].encode()):
            user_id = user[0]
            jwt_token = jwt.encode({'payloads': user_id}, app.config['SECRET_KEY'], algorithm="HS256")
            response = make_response(jsonify({'message': 'Successfully logged in', 'accessToken': f'{jwt_token}'}), 200)
            return response
        return make_response(jsonify({'error': 'Invalid credentials'}), 401)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route("/api/v1/auth/register", methods=['POST'])
def register():
    try:
        email, password = request.json['email'], request.json['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE email = %s", (email,))
        if cur.fetchone():
            return make_response(jsonify({'error': 'User with this email already exists'}), 400)

        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())

        cur.execute("INSERT INTO persons (ID, email, password) VALUES (%s, %s, %s)", (user_id, email, hash_password))
        mysql.connection.commit()

        jwt_token = jwt.encode({'payloads': user_id}, app.config['SECRET_KEY'], algorithm="HS256")
        response = make_response(jsonify({'message': 'Successfully registered', 'accessToken': f'{jwt_token}'}), 200)
        return response
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route("/api/v1/surveys/create", methods=['POST'])
def create_survey():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['payloads']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        survey_title = request.json['title']
        survey_id = str(uuid.uuid4())

        cur.execute("INSERT INTO surveys (ID, owner_ID, title) VALUES (%s, %s, %s)",
                    (survey_id, owner_id, survey_title))
        mysql.connection.commit()

        return make_response(jsonify({'surveyId': survey_id}), 200)
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route("/api/v1/surveys/<survey_id>", methods=['GET'])
def get_survey(survey_id):
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['payloads']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        cur.execute(f'SELECT * FROM surveys WHERE ID = "{survey_id}"')
        test_data = cur.fetchone()
        test_info = {'surveyID': test_data[0], 'ownerID': test_data[1], 'title': test_data[2]}

        cur.execute(f'SELECT * FROM questions WHERE survey_ID = "{survey_id}"')
        test_questions_data = cur.fetchall()
        test_questions_info = [i[0] for i in test_questions_data]
        if test_questions_info:
            test_info['questions'] = test_questions_info
            test_info['questions_number'] = len(test_questions_info)
            return make_response(jsonify(test_info), 200)
        else:
            return make_response(jsonify({'error': 'Questions list is empty'}), 404)

    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route("/api/v1/surveys/questions/<question_id>", methods=['GET'])
def get_question(question_id):
    # jwt_token = get_jwt_token()
    # if not jwt_token:
    #     return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        # payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        # owner_id = payload['payloads']
        #
        cur = mysql.connection.cursor()
        # cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        # if not cur.fetchone():
        #     return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        cur.execute(f'SELECT * FROM questions WHERE ID = "{question_id}"')
        data = cur.fetchone()
        question_info = {'questionID': data[0], 'surveyID': data[1], 'text': data[2], 'type': data[3]}

        cur.execute(f'SELECT * FROM answers WHERE question_ID = "{question_id}"')
        question_answers_data = cur.fetchall()
        question_answers_info = [[i for i in answer] for answer in question_answers_data]
        if question_answers_info:
            question_info['answers'] = question_answers_info
            return make_response(jsonify(question_info), 200)
        else:
            return make_response(jsonify({'error': 'Answers list is empty'}), 404)

    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == "__main__":
    app.run(debug=True)
