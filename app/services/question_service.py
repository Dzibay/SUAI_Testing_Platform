from app import db
from app.models import Question

class QuestionService:
    @staticmethod
    def create_question(data):
        new_question = Question(
            title=data['title'],
            type=data['type'],
            test_id=data['test_id'],
            order=data['order'],
            test_type=data['test_type'],
            required=data['required']
        )
        db.session.add(new_question)
        db.session.commit()
        return new_question

    @staticmethod
    def update_question(question_id, data):
        question = Question.query.get_or_404(question_id)
        for key, value in data.items():
            setattr(question, key, value)
        db.session.commit()
        return question

    @staticmethod
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
