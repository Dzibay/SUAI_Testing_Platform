from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# class Test(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#
#     def __repr__(self):
#         return '<Test %r>' % self.id


# @app.route('/api/main/get_info/<int:id_>', methods=['GET'])
# def get_info(id_):
#     return id_
#
#
# @app.route('/api/main/create', methods=['POST'])
# def create():
#     title = request.form['title']
#
#
# if __name__ == "__main__":
#     app.run(debug=True)


