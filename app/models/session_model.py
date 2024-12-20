from datetime import datetime, timezone

from sqlalchemy import ARRAY
from sqlalchemy.dialects.mysql import JSON

from app import db
import uuid

class Session(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = db.Column(db.String(36), db.ForeignKey('test.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'completed'
    answers = db.Column(db.Text, nullable=True, default="")
    current_question_id = db.Column(db.String(36), nullable=True)
    next_question_id = db.Column(db.String(36), nullable=True)
    time_spent = db.Column(db.Interval, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_inputs = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Session {self.id}>'
