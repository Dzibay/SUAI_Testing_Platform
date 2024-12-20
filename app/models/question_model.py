from datetime import datetime, timezone
from app import db
import uuid

class Question(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'radio', 'checkbox', 'textarea'
    test_id = db.Column(db.String(36), db.ForeignKey('test.id'), nullable=False)
    test_type = db.Column(db.String(36), nullable=False)
    created_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.title}>'
