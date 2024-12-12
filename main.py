from typing import List, Dict
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_cors import CORS
import bcrypt
import uuid
import jwt

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "surveity"
app.config['SECRET_KEY'] = 'SECRET_KEY'

mysql = MySQL(app)

def create_tables():
    with app.app_context():
        cur = mysql.connection.cursor()
        # Create persons table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                ID VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        # Create surveys table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                ID VARCHAR(36) PRIMARY KEY,
                owner_ID VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                status VARCHAR(50) NOT NULL,
                FOREIGN KEY (owner_ID) REFERENCES persons(ID)
            )
        """)
        # Create questions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                ID VARCHAR(36) PRIMARY KEY,
                survey_ID VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                FOREIGN KEY (survey_ID) REFERENCES surveys(ID)
            )
        """)
        # Create answers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                ID VARCHAR(36) PRIMARY KEY,
                question_ID VARCHAR(36) NOT NULL,
                text VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                FOREIGN KEY (question_ID) REFERENCES questions(ID)
            )
        """)
        # Create sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                ID VARCHAR(36) PRIMARY KEY,
                survey_ID VARCHAR(36) NOT NULL,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_ID) REFERENCES surveys(ID)
            )
        """)
        mysql.connection.commit()
        cur.close()


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
        user_id = payload['id']

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
            jwt_token = jwt.encode({'id': user_id}, app.config['SECRET_KEY'], algorithm="HS256")
            response = make_response(jsonify({'message': 'Successfully logged in', 'accessToken': jwt_token}), 200)
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

        jwt_token = jwt.encode({'id': user_id}, app.config['SECRET_KEY'], algorithm="HS256")
        response = make_response(jsonify({'message': 'Successfully registered', 'accessToken': jwt_token}), 200)
        return response
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys", methods=['POST'])
def create_survey():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        survey_title = request.json.get('title')
        start_date_str = request.json.get('startDate')
        end_date_str = request.json.get('endDate')

        if not survey_title:
            return make_response(jsonify({'error': 'Title is missing'}), 400)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        status = 'pending'
        questions: List = request.json.get('questions', [])
        survey_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO surveys (ID, owner_ID, title, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (survey_id, owner_id, survey_title, start_date, end_date, status))

        for question in questions:
            question_id = str(uuid.uuid4())
            name = question.get('name', '')
            questionType = question.get('type', '')
            cur.execute("""
                INSERT INTO questions (ID, survey_ID, name, type)
                VALUES (%s, %s, %s, %s)
            """, (question_id, survey_id, name, questionType))

            for answer in question.get('answers', []):
                answer_id = str(uuid.uuid4())
                answer_text = answer.get('text', '')
                answer_type = answer.get('type', '')
                cur.execute("""
                    INSERT INTO answers (ID, question_ID, text, type)
                    VALUES (%s, %s, %s, %s)
                """, (answer_id, question_id, answer_text, answer_type))

        mysql.connection.commit()

        return make_response(jsonify({'surveyId': survey_id}), 200)
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        app.logger.error(f"Error creating survey: {str(e)}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/", methods=['GET'])
def get_user_surveys():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['id']

        # Используем курсор с DictCursor
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        # Fetch all surveys for the user
        cur.execute("SELECT * FROM surveys WHERE owner_ID = %s", (owner_id,))
        surveys = cur.fetchall()

        if not surveys:
            return make_response(jsonify({'error': 'No surveys found for the user'}), 404)

        surveys_data = []

        for survey in surveys:
            survey_id = survey['ID']
            survey_info = {
                'id': survey_id,
                'owner': survey['owner_ID'],
                'title': survey['title'],
                'startDate': survey['start_date'].isoformat(),
                'endDate': survey['end_date'].isoformat(),
                'status': survey['status'],
                'questions': []
            }

            # Fetch questions for the survey
            cur.execute("SELECT * FROM questions WHERE survey_ID = %s", (survey_id,))
            questions = cur.fetchall()

            if not questions:
                survey_info['questions'] = []
            else:
                for question in questions:
                    question_id = question['ID']
                    question_info = {
                        'id': question_id,
                        'name': question['name'],
                        'type': question['type'],
                        'answers': []
                    }

                    # Fetch answers for the question
                    cur.execute("SELECT * FROM answers WHERE question_ID = %s", (question_id,))
                    answers = cur.fetchall()

                    if not answers:
                        question_info['answers'] = []
                    else:
                        for answer in answers:
                            answer_info = {
                                'text': answer['text'],
                                'type': answer['type']
                            }
                            question_info['answers'].append(answer_info)

                    survey_info['questions'].append(question_info)

            surveys_data.append(survey_info)

        return make_response(jsonify(surveys_data), 200)

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
        owner_id = payload['id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        cur.execute('SELECT * FROM surveys WHERE ID = %s', (survey_id,))
        survey_data = cur.fetchone()
        if not survey_data:
            return make_response(jsonify({'error': 'Survey not found'}), 404)

        survey_info = {
            'id': survey_data[0],
            'owner': survey_data[1],
            'title': survey_data[2],
            'startDate': survey_data[3].isoformat(),
            'endDate': survey_data[4].isoformat(),
            'status': survey_data[5],
            'questions': []
        }

        cur.execute('SELECT * FROM questions WHERE survey_ID = %s', (survey_id,))
        questions_data = cur.fetchall()

        for question in questions_data:
            question_info = {
                'id': question[0],
                'name': question[2],
                'type': 'text',
                'text': question[2],
                'answers': []
            }

            cur.execute('SELECT * FROM answers WHERE question_ID = %s', (question[0],))
            answers_data = cur.fetchall()

            for answer in answers_data:
                answer_info = {
                    'text': answer[2],
                    'type': 'radio',
                    'isCorrect': answer[3]
                }
                question_info['answers'].append(answer_info)

            survey_info['questions'].append(question_info)

        return make_response(jsonify(survey_info), 200)

    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/questions/<question_id>", methods=['GET'])
def get_question(question_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM questions WHERE ID = %s', (question_id,))
        question_data = cur.fetchone()
        if not question_data:
            return make_response(jsonify({'error': 'Question not found'}), 404)

        question_info = {
            'questionID': question_data[0],
            'surveyID': question_data[1],
            'text': question_data[2]
        }

        cur.execute('SELECT * FROM answers WHERE question_ID = %s', (question_id,))
        answers_data = cur.fetchall()
        if not answers_data:
            return make_response(jsonify({'error': 'Answers not found'}), 404)

        question_info['answers'] = [{'answerID': ans[0], 'text': ans[2], 'is_correct': ans[3]} for ans in answers_data]

        return make_response(jsonify(question_info), 200)

    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/<survey_id>", methods=['DELETE'])
def delete_survey(survey_id):
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        cur.execute('SELECT * FROM surveys WHERE ID = %s AND owner_ID = %s', (survey_id, owner_id))
        survey_data = cur.fetchone()
        if not survey_data:
            return make_response(jsonify({'error': 'Survey not found or you do not have permission to delete it'}), 404)

        # Delete related answers
        cur.execute('DELETE FROM answers WHERE question_ID IN (SELECT ID FROM questions WHERE survey_ID = %s)', (survey_id,))

        # Delete related questions
        cur.execute('DELETE FROM questions WHERE survey_ID = %s', (survey_id,))

        # Delete the survey
        cur.execute('DELETE FROM surveys WHERE ID = %s', (survey_id,))

        mysql.connection.commit()

        return make_response(jsonify({'message': 'Survey deleted successfully'}), 200)

    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/<survey_id>", methods=['PUT'])
def update_survey(survey_id):
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['id']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM persons WHERE ID = %s", (owner_id,))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Invalid authentication token'}), 403)

        cur.execute('SELECT * FROM surveys WHERE ID = %s AND owner_ID = %s', (survey_id, owner_id))
        survey_data = cur.fetchone()
        if not survey_data:
            return make_response(jsonify({'error': 'Survey not found or you do not have permission to update it'}), 404)

        survey_title = request.json.get('title')
        start_date_str = request.json.get('startDate')
        end_date_str = request.json.get('endDate')
        status = request.json.get('status')
        questions: List = request.json.get('questions', [])

        if not survey_title:
            return make_response(jsonify({'error': 'Title is missing'}), 400)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        cur.execute("""
            UPDATE surveys
            SET title = %s, start_date = %s, end_date = %s, status = %s
            WHERE ID = %s
        """, (survey_title, start_date, end_date, status, survey_id))

        # Handle questions and answers
        existing_question_ids = set()
        cur.execute("SELECT ID FROM questions WHERE survey_ID = %s", (survey_id,))
        for row in cur.fetchall():
            existing_question_ids.add(row[0])

        for question in questions:
            question_id = question.get('id')
            name = question.get('name', '')
            questionType = question.get('type', '')
            answers = question.get('answers', [])

            if question_id:
                # Update existing question
                cur.execute("""
                    UPDATE questions
                    SET name = %s, type = %s
                    WHERE ID = %s
                """, (name, questionType, question_id))
                existing_question_ids.discard(question_id)
            else:
                # Insert new question
                question_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO questions (ID, survey_ID, name, type)
                    VALUES (%s, %s, %s, %s)
                """, (question_id, survey_id, name, questionType))

            # Handle answers for the question
            existing_answer_ids = set()
            cur.execute("SELECT ID FROM answers WHERE question_ID = %s", (question_id,))
            for row in cur.fetchall():
                existing_answer_ids.add(row[0])

            for answer in answers:
                answer_id = answer.get('id')
                answer_text = answer.get('text', '')
                answer_type = answer.get('type', '')

                if answer_id:
                    # Update existing answer
                    cur.execute("""
                        UPDATE answers
                        SET text = %s, type = %s
                        WHERE ID = %s
                    """, (answer_text, answer_type, answer_id))
                    existing_answer_ids.discard(answer_id)
                else:
                    # Insert new answer
                    answer_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO answers (ID, question_ID, text, type)
                        VALUES (%s, %s, %s, %s)
                    """, (answer_id, question_id, answer_text, answer_type))

            # Delete remaining answers
            for answer_id in existing_answer_ids:
                cur.execute("DELETE FROM answers WHERE ID = %s", (answer_id,))

        # Delete remaining questions
        for question_id in existing_question_ids:
            cur.execute("DELETE FROM questions WHERE ID = %s", (question_id,))

        mysql.connection.commit()

        return make_response(jsonify({'message': 'Survey updated successfully'}), 200)

    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/link", methods=["POST"])
def generate_survey_link():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return make_response(jsonify({'error': 'Authentication token is missing'}), 401)

    try:
        payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        owner_id = payload['id']

        survey_id = request.json.get('surveyId')
        if not survey_id:
            return make_response(jsonify({'error': 'Survey ID is required'}), 400)

        # Check if the survey exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM surveys WHERE ID = %s AND owner_ID = %s", (survey_id, owner_id))
        if not cur.fetchone():
            return make_response(jsonify({'error': 'Survey not found or not authorized'}), 404)

        # Create payload for the link
        link_payload = {
            "survey_id": survey_id,
            "exp": datetime.utcnow() + timedelta(days=1)  # Link valid for 1 day
        }
        token = jwt.encode(link_payload, app.config['SECRET_KEY'], algorithm="HS256")

        # Generate the link
        survey_link = f"http://localhost:5173/survey/{token}"
        return make_response(jsonify({'link': survey_link}), 200)
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/start/<token>", methods=["GET"])
def start_survey(token):
    try:
        # Decode the token to get survey details
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        survey_id = payload['survey_id']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM surveys WHERE ID = %s", (survey_id,))
        survey = cur.fetchone()

        if not survey:
            return make_response(jsonify({'error': 'Survey not found'}), 404)

        # Create a session for the user
        session_id = str(uuid.uuid4())
        cur.execute("INSERT INTO sessions (ID, survey_ID) VALUES (%s, %s)", (session_id, survey_id))
        mysql.connection.commit()

        return make_response(jsonify({
            'sessionId': session_id,
            'surveyTitle': survey['title'],
            'startDate': survey['start_date'].isoformat(),
            'endDate': survey['end_date'].isoformat(),
            'status': survey['status']
        }), 200)
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'error': 'Token expired'}), 403)
    except jwt.InvalidTokenError:
        return make_response(jsonify({'error': 'Invalid token'}), 403)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route("/api/v1/surveys/<survey_id>/questions/next", methods=["GET"])
def get_next_question(survey_id):
    session_id = request.headers.get("Session-ID")
    if not session_id:
        return make_response(jsonify({'error': 'Session ID is required'}), 400)

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Get next unanswered question
        cur.execute("""
            SELECT q.* FROM questions q
            LEFT JOIN user_answers ua ON q.ID = ua.question_ID AND ua.session_ID = %s
            WHERE q.survey_ID = %s AND ua.ID IS NULL
            LIMIT 1
        """, (session_id, survey_id))
        question = cur.fetchone()

        if not question:
            return make_response(jsonify({'message': 'No more questions'}), 200)

        return make_response(jsonify({
            'questionId': question['ID'],
            'text': question['name'],
            'type': question['type']
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route("/api/v1/surveys/<survey_id>/answer", methods=["POST"])
def submit_answer(survey_id):
    session_id = request.headers.get("Session-ID")
    if not session_id:
        return make_response(jsonify({'error': 'Session ID is required'}), 400)

    try:
        data = request.json
        question_id = data.get('questionId')
        answer_text = data.get('answer')

        if not question_id or not answer_text:
            return make_response(jsonify({'error': 'Question ID and answer are required'}), 400)

        # Save the answer
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO user_answers (ID, session_ID, question_ID, answer)
            VALUES (%s, %s, %s, %s)
        """, (str(uuid.uuid4()), session_id, question_id, answer_text))
        mysql.connection.commit()

        return make_response(jsonify({'message': 'Answer submitted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
