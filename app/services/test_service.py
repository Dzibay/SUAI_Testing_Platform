import flask
from sqlalchemy.exc import NoResultFound

from app import db, jwt
from app.models import Test, Question, Answer, Session
import json
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, decode_token
from flask import current_app, app
import pytz
import jwt

from app.services.answer_service import AnswerService
from app.services.question_service import QuestionService

class TestService:
    @staticmethod
    def create_test(user_id, data):
        options = data.get('options', {})
        description = data['description'] if options.get('description') else None
        user_inputs = json.dumps(data['user_inputs']) if not options.get('user_inputs') else None
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('end_date') else None
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('start_date') else None

        new_test = Test(
            title=data['title'],
            description=description,
            type=data['type'],
            options=json.dumps(options),
            user_inputs=user_inputs,
            end_date=end_date,
            start_date=start_date,
            user_id=user_id
        )

        if options.get('password'):
            new_test.set_password(data['password'])
        if options.get('complete_time'):
            new_test.set_complete_time(data['complete_time'])

        db.session.add(new_test)
        db.session.commit()
        return new_test

    @staticmethod
    def create_test_with_questions_and_answers(data, questions_data):
        new_test = TestService.create_test(data.get('user_id') ,data)

        for question_data in questions_data:
            question_data['test_id'] = new_test.id
            question = QuestionService.create_question(question_data)

            for answer_data in question_data.get('answers', []):
                AnswerService.create_answer(question.id, answer_data)

        return new_test

    @staticmethod
    def update_test(test_id, data):
        test = Test.query.get_or_404(test_id)
        for key, value in data.items():
            if key == 'options':
                test.options = json.dumps(value)
            elif key == 'user_inputs':
                test.user_inputs = json.dumps(value)
            elif key == 'end_date' or key == 'start_date':
                setattr(test, key, datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ'))
            elif key == 'complete_time':
                test.set_complete_time(value)
            elif key == 'title':
                test.title = value
            # else:
            #     setattr(test, key, value)
        db.session.commit()
        return test

    @staticmethod
    def update_test_with_questions_and_answers(test_id, data, questions_data):
        # Update the test
        test = TestService.update_test(test_id, data)

        # Delete all existing questions and answers for the test
        Question.query.filter_by(test_id=test_id).delete()
        db.session.commit()

        # Create new questions and answers
        for question_data in questions_data:
            question_data['test_id'] = test_id
            question = QuestionService.create_question(question_data)

            for answer_data in question_data.get('answers', []):
                AnswerService.create_answer(question.id, answer_data)

        return test

    @staticmethod
    def delete_test(test_id):
        test = Test.query.get_or_404(test_id)
        db.session.delete(test)
        db.session.commit()

    @staticmethod
    def get_all_tests(user_id):
        tests = Test.query.filter_by(user_id=user_id).all()
        return [{
            "id": test.id,
            "title": test.title,
            "start_date": test.start_date,
            "end_date": test.end_date,
            "type": test.type,
            "question_count": len(test.questions)
        } for test in tests]

    # def verify_survey_link(token):
    #     try:
    #         payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    #         return payload
    #     except jwt.ExpiredSignatureError:
    #         return None  # Токен истек
    #     except jwt.InvalidTokenError:
    #         return None  # Неверный токен

    @staticmethod
    def get_test_by_id(test_id, user_id):
        test = Test.query.filter_by(id=test_id, user_id=user_id).first_or_404()
        questions = Question.query.filter_by(test_id=test_id).order_by(Question.order).all()
        test_data = {
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "complete_time": test.complete_time,
            "user_inputs": test.user_inputs_list,
            "type": test.type,
            "options": test.options_dict,
            "end_date": test.end_date,
            "start_date": test.start_date,
            "questions": [],
            "tgLink": test.tgLink,
            "webLink": test.webLink,
        }
        for question in questions:
            answers = Answer.query.filter_by(question_id=question.id).all()
            question_data = {
                "id": question.id,
                "title": question.title,
                "type": question.type,
                "order": question.order,
                "test_type": question.test_type,
                "required": question.required,
                "answers": [{
                    "id": answer.id,
                    "text": answer.text,
                    "is_correct": answer.is_correct
                } for answer in answers]
            }
            test_data["questions"].append(question_data)
        return test_data

    @staticmethod
    def generate_test_link(test_id, link_type, lifetime):
        test = Test.query.get_or_404(test_id)
        test.auth_token = None
        db.session.commit()

        payload = {
            'test_id': test_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=lifetime or 2),
            'sub': 'web'
        }

        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        test.auth_token = token
        db.session.commit()

        if link_type == 'web':
            base_url = current_app.config['WEB_BASE_URL']
            link = f"{base_url}/test?token={token}"
            test.webLink = link
            db.session.commit()
            return link
        elif link_type == 'telegram':
            bot_name = current_app.config['TELEGRAM_BOT_NAME']
            link = f"https://t.me/{bot_name}?start={test_id}"
            test.tgLink = link
            db.session.commit()
            return link
        else:
            return None

    @staticmethod
    def close_test_link(test_id, link_type):
        test = Test.query.get_or_404(test_id)
        test.auth_token = None

        if link_type == 'web':
            test.webLink = None
        if link_type == 'telegram':
            test.tgLink = None

        db.session.commit()


    @staticmethod
    def get_test_by_token(token):
        try:
            decoded_token = decode_token(token)
            test_id = decoded_token['sub']
            test = Test.query.get_or_404(test_id)
            if test.auth_token != token:
                return None, "Link has been updated. Please use the new link."
            return test, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_test_summary_by_token(token):
        try:

            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']
            token_sub = decoded_token['sub']
            test = Test.query.get_or_404(test_id)
            if test.auth_token != token and token_sub != 'telegramSurveityBot':
                return None, "Link has been updated. Please use the new link."

            # existing_session = Session.query.filter_by(test_id=test_id, status='completed').first()
            # if existing_session and not test.options_dict.get('allow_multiple_submissions', False):
            #     return None, "You have already completed the test."

            questions = Question.query.filter_by(test_id=test_id).order_by(Question.order).all()
            return {
                "id": test.id,
                "title": test.title,
                "start_date": test.start_date,
                "end_date": test.end_date,
                "options": json.loads(test.options),
                "description": test.description,
                "type": test.type,
                "question_count": len(questions),
                "user_inputs": json.loads(test.user_inputs),
                "complete_time": test.complete_time,
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_session(token, session_id):
        try:
            # Декодирование токена
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']

            # Поиск существующей сессии
            existing_session = Session.query.get_or_404(session_id)

            if existing_session:
                # Убедитесь, что created_at имеет информацию о часовом поясе
                if existing_session.created_at.tzinfo is None:
                    existing_session.created_at = existing_session.created_at.replace(tzinfo=timezone.utc)

                # Обновление времени, проведенного в сессии
                existing_session.time_spent = datetime.now(timezone.utc) - existing_session.created_at
                db.session.commit()
                return existing_session, None

            return None, "Session not found."
        except jwt.ExpiredSignatureError:
            return None, "Signature has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."
        except NoResultFound:
            return None, "Test not found."
        except Exception as e:
            return None, str(e)

    @staticmethod
    def create_session(token, session_data, userInputs):
        try:
            # Декодирование токена
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']

            # Получение теста по test_id
            test = Test.query.get_or_404(test_id)
            token_sub = decoded_token['sub']

            if test.auth_token != token and token_sub != 'telegramSurveityBot':
                return None, "Link has been updated. Please use the new link."

            # Проверка, что userInputs не является NULL, если test.user_inputs также не является NULL
            if test.user_inputs is not None and userInputs is None:
                return None, "userInputs cannot be NULL when test.user_inputs is not NULL."

            # Сериализация userInputs в строку JSON
            user_inputs_json = json.dumps(userInputs)

            new_session = Session(
                test_id=test_id,
                status='start',
                current_question_id=None,
                time_spent=datetime.now(timezone.utc) - datetime.now(timezone.utc),
                user_inputs=user_inputs_json  # Добавление userInputs в новую сессию
            )
            db.session.add(new_session)
            db.session.commit()
            return new_session.id, None

        except jwt.ExpiredSignatureError:
            return None, "Signature has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."
        except NoResultFound:
            return None, "Test not found."
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_next_question(session_id, token):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']
        except jwt.ExpiredSignatureError:
            return None, "Token has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."

        test = Test.query.get_or_404(test_id)
        token_sub = decoded_token['sub']
        if test.auth_token != token and token_sub != 'telegramSurveityBot':
            return None, "Link has been updated. Please use the new link."

        session = Session.query.filter_by(test_id=test_id, id=session_id).first()
        if not session:
            return None, "Session not found."

        next_question_id = session.next_question_id
        if next_question_id:
            next_question = Question.query.get_or_404(next_question_id)
        else:
            next_question = None

        if next_question:
            session.current_question_id = next_question.id
            following_question = Question.query.filter(
                Question.test_id == session.test_id,
                Question.order > next_question.order
            ).order_by(Question.order).first()

            session.next_question_id = following_question.id if following_question else None
        else:
            session.current_question_id = None
            session.next_question_id = None

        db.session.commit()

        if next_question:
            return {
                "question_id": next_question.id,
                "isLast": session.next_question_id is None,
                "text": next_question.title,
                "type": next_question.type,
                "order": next_question.order,
                "answers": [{
                    "id": answer.id,
                    "text": answer.text
                } for answer in next_question.answers]
            }, None
        else:
            return None, "No more questions available."

    @staticmethod
    def submit_answer(session_id, question_id, answer_id):
        session = Session.query.get_or_404(session_id)
        if session.status == 'completed':
            return "Test has been completed.", 400

        answers = session.answers or ""
        answers += f"{question_id}:{answer_id};"
        session.answers = answers
        utc = pytz.UTC
        current_question = Question.query.get_or_404(question_id)

        next_question = Question.query.filter(Question.test_id == session.test_id, Question.order > current_question.order).first()
        if not next_question:
            session.created_at = utc.localize(session.created_at)
            session.status = 'completed'
            session.time_spent = datetime.now(timezone.utc) - session.created_at

        db.session.commit()
        return None

    @staticmethod
    def complete_test(session_id):
        session = Session.query.get_or_404(session_id)
        session.status = 'completed'
        utc = pytz.UTC
        session.created_at = utc.localize(session.created_at)
        session.time_spent = datetime.now(timezone.utc) - session.created_at
        db.session.commit()
        return None

    @staticmethod
    def init_session(token, session_id):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']
            test = Test.query.get_or_404(test_id)
            if test.auth_token != token:
                return None, "Link has been updated. Please use the new link."

            existing_session = Session.query.filter_by(test_id=test_id, id=session_id).first()
            if existing_session:
                return existing_session, None
            else:
                return None, "Session not found."
        except jwt.ExpiredSignatureError:
            return None, "Signature has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."
        except NoResultFound:
            return None, "Test not found."
        except Exception as e:
            return None, str(e)

    @staticmethod
    def start_test(token, session_id):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']
            token_sub = decoded_token['sub']
            test = Test.query.get_or_404(test_id)
            if test.auth_token != token and token_sub != 'telegramSurveityBot':
                return None, "Link has been updated. Please use the new link."

            session = Session.query.filter_by(test_id=test_id, id=session_id).first()
            if not session:
                return None, "Session not found."

            current_question_id = session.current_question_id
            if current_question_id:
                current_question = Question.query.get_or_404(current_question_id)
            else:
                current_question = Question.query.filter_by(test_id=session.test_id).order_by(Question.order).first()

            next_question = Question.query.filter(
                Question.test_id == session.test_id,
                Question.order > current_question.order
            ).order_by(Question.order).first()

            if next_question:
                session.current_question_id = current_question.id
                session.next_question_id = next_question.id
            else:
                session.current_question_id = current_question.id
                session.next_question_id = None
            db.session.commit()

            if next_question:
                return {
                    "question_id": current_question.id,
                    "isLast": next_question is None,
                    "text": current_question.title,
                    "type": current_question.type,
                    "order": current_question.order,
                    "answers": [{
                        "id": answer.id,
                        "text": answer.text
                    } for answer in current_question.answers]
                }, None
            else:
                return None, "No more questions available."
        except jwt.ExpiredSignatureError:
            return None, "Signature has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."
        except NoResultFound:
            return None, "Test not found."
        except Exception as e:
            return None, str(e)

    @staticmethod
    def continue_test(token, session_id):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            test_id = decoded_token['test_id']
            test = Test.query.get_or_404(test_id)
            if test.auth_token != token:
                return None, "Link has been updated. Please use the new link."

            session = Session.query.filter_by(test_id=test_id, id=session_id).first()
            if not session:
                return None, "Session not found."

            current_question_id = session.current_question_id
            if current_question_id:
                current_question = Question.query.get_or_404(current_question_id)
            else:
                current_question = Question.query.filter_by(test_id=test_id).order_by(Question.order).first()

            if not current_question:
                return None, "No questions available."

            return {
                "question_id": current_question.id,
                "text": current_question.title,
                "isLast": session.next_question_id is None,
                "type": current_question.type,
                "order": current_question.order,
                "answers": [{
                    "id": answer.id,
                    "text": answer.text
                } for answer in current_question.answers]
            }, None
        except jwt.ExpiredSignatureError:
            return None, "Signature has expired."
        except jwt.InvalidTokenError:
            return None, "Invalid token."
        except NoResultFound:
            return None, "Test not found."
        except Exception as e:
            return None, str(e)
