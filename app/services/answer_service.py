from app import db
from app.models import Answer, Test, Session


class AnswerService:
    @staticmethod
    def create_answer(question_id, data):
        new_answer = Answer(
            text=data['text'],
            question_id=question_id,
            is_correct=data.get('is_correct')
        )
        db.session.add(new_answer)
        db.session.commit()
        return new_answer

    @staticmethod
    def update_answer(answer_id, data):
        answer = Answer.query.get_or_404(answer_id)
        for key, value in data.items():
            setattr(answer, key, value)
        db.session.commit()
        return answer

    @staticmethod
    def delete_answer(answer_id):
        answer = Answer.query.get_or_404(answer_id)
        db.session.delete(answer)
        db.session.commit()

    @staticmethod
    def get_test_answers(test_id):
        results = Session.query.filter_by(test_id=test_id).all()
        return results

