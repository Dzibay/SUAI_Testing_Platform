import uuid
from sqlite3 import OperationalError
import jwt
from pydantic import ValidationError
from datetime import datetime
from models.types.Survey import Survey

def create_survey(mysql, token, data, config):
    try:
        survey_id = str(uuid.uuid4())
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])

        # Parse datetime strings into datetime objects
        start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00'))

        survey_data = Survey(
            id=survey_id,
            owner=payload['id'],
            title=data['title'],
            startDate=start_date,
            endDate=end_date,
            status=data['status'],
            questions=[]
        )

        # Format datetime objects for database insertion
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO surveys (ID, owner_ID, title, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (survey_id, payload['id'], data['title'], start_date_str, end_date_str, data['status'])
        )

        # Insert questions into the child table
        for question in data.get('questions', []):
            question_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO questions (ID, survey_ID, name, type, `order`) VALUES (%s, %s, %s, %s, %s)",
                (question_id, survey_id, question['name'], question['type'], question['order'])
            )

            # Insert answers for each question
            for answer in question.get('answers', []):
                answer_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO answers (ID, question_ID, text, type) VALUES (%s, %s, %s, %s)",
                    (answer_id, question_id, answer['text'], answer['type'])
                )

        mysql.connection.commit()
        cur.close()

        return {'message': 'Survey created', 'surveyId': survey_id}

    except OperationalError as e:
        return {'error': 'Database error', 'details': str(e)}, 500

    except KeyError as e:
        return {'error': 'Missing key in request data', 'details': str(e)}, 400

    except ValidationError as e:
        return {'error': 'Validation error', 'details': e.errors()}, 400

    except Exception as e:
        return {'error': 'Unexpected error', 'details': str(e)}, 500

def get_surveys(mysql, token, config):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM surveys WHERE owner_ID = %s",
            (payload['id'],)
        )
        surveys_data = cur.fetchall()

        surveys = []
        for survey_data in surveys_data:
            survey_id = survey_data[0]
            cur.execute(
                "SELECT * FROM questions WHERE survey_ID = %s ORDER BY `order`",
                (survey_id,)
            )
            questions_data = cur.fetchall()
            questions = []
            for question_data in questions_data:
                question_id = question_data[0]
                cur.execute(
                    "SELECT * FROM answers WHERE question_ID = %s",
                    (question_id,)
                )
                answers_data = cur.fetchall()
                answers = [{'id': a[0], 'text': a[2], 'type': a[3]} for a in answers_data]
                print(question_data)
                questions.append({'id': question_data[0], 'name': question_data[2], 'type': question_data[4], 'order': question_data[3], 'answers': answers})

            survey = Survey(
                id=survey_data[0],
                owner=survey_data[1],
                title=survey_data[2],
                startDate=survey_data[3],
                endDate=survey_data[4],
                status=survey_data[5],
                questions=questions
            )
            surveys.append(survey.dict())

        cur.close()

        return {'surveys': surveys}

    except OperationalError as e:
        return {'error': 'Database error', 'details': str(e)}, 500

    except Exception as e:
        return {'error': 'Unexpected error', 'details': str(e)}, 500

def update_survey(mysql, token, data, config):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        survey_id = data['id']

        # Parse datetime strings into datetime objects
        start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00'))

        # Format datetime objects for database insertion
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE surveys SET title = %s, start_date = %s, end_date = %s, status = %s WHERE ID = %s AND owner_ID = %s",
            (data['title'], start_date_str, end_date_str, data['status'], survey_id, payload['id'])
        )

        # Delete existing questions and answers
        cur.execute(
            "DELETE FROM questions WHERE survey_ID = %s",
            (survey_id,)
        )

        # Insert new questions and answers
        for question in data.get('questions', []):
            question_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO questions (ID, survey_ID, name, type, `order`) VALUES (%s, %s, %s, %s, %s)",
                (question_id, survey_id, question['name'], question['type'], question['order'])
            )

            for answer in question.get('answers', []):
                answer_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO answers (ID, question_ID, text, type) VALUES (%s, %s, %s, %s)",
                    (answer_id, question_id, answer['text'], answer['type'])
                )

        mysql.connection.commit()
        cur.close()

        return {'message': 'Survey updated'}

    except OperationalError as e:
        return {'error': 'Database error', 'details': str(e)}, 500

    except Exception as e:
        return {'error': 'Unexpected error', 'details': str(e)}, 500

def delete_survey(mysql, token, survey_id, config):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        cur = mysql.connection.cursor()

        cur.execute(
            "DELETE FROM surveys WHERE ID = %s AND owner_ID = %s",
            (survey_id, payload['id'])
        )

        mysql.connection.commit()
        cur.close()

        return {'message': 'Survey deleted'}

    except OperationalError as e:
        return {'error': 'Database error', 'details': str(e)}, 500

    except Exception as e:
        return {'error': 'Unexpected error', 'details': str(e)}, 500
