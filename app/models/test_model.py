from datetime import datetime, timezone
from app import db
from app.utils.password_utils import generate_password_hash, check_password_hash
import uuid
import json

class Test(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(256))
    complete_time = db.Column(db.String(128), nullable=True, default='')
    type = db.Column(db.String(10), nullable=False)  # 'test' or 'survey'
    options = db.Column(db.Text, nullable=True, default="{}")
    user_inputs = db.Column(db.Text, nullable=True, default="[]")
    end_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    webLink = db.Column(db.Text, default=None)
    tgLink = db.Column(db.Text, default=None)
    auth_token = db.Column(db.String(512), nullable=True)

    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')

    def set_complete_time(self, complete_time):
        self.complete_time = str(complete_time.get('hours')) + ":" + str(complete_time.get('minutes')) + ":" + str(complete_time.get('seconds'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Test {self.title}>'

    @property
    def options_dict(self):
        return json.loads(self.options)

    @options_dict.setter
    def options_dict(self, value):
        self.options = json.dumps(value)

    @property
    def user_inputs_list(self):
        return json.loads(self.user_inputs)

    @user_inputs_list.setter
    def user_inputs_list(self, value):
        self.user_inputs = json.dumps(value)
