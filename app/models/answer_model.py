from datetime import datetime, timezone
from app import db
import uuid

class Answer(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=True)
    question_id = db.Column(db.String(36), db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Answer {self.text}>'
