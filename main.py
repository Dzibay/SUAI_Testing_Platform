from flask import Flask, request, Response
from flask_mysqldb import MySQL
import json
import bcrypt
import uuid
import jwt


app = Flask(__name__)

# Required
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "database"
app.config['SECRET_KEY'] = 'SECRET_KEY'

mysql = MySQL(app)


@app.route("/api/v1/auth/authentication", methods=['POST'])
def authentication():
    jwt_token = None
    if "Authorization" in request.headers:
        jwt_token = request.headers["Authorization"].split(" ")[1]
    if not jwt_token:
        return Response('Authentication Token is missing!', status=401, mimetype='text/xml')

    user_id = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])['payloads']

    cur = mysql.connection.cursor()
    count_users_with_this_id = cur.execute(f"""SELECT * FROM `database`.`persons` WHERE ID = '{user_id}'""")
    if count_users_with_this_id == 1:
        return Response('', status=200, mimetype='text/xml')
    else:
        return Response('Not valid authentication token!', status=403, mimetype='text/xml')


@app.route("/api/v1/auth/login", methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    email, password = request.json['email'], request.json['password']
    cur.execute(f"""SELECT ID, password FROM persons WHERE email = '{email}'""")
    database_response = cur.fetchall()

    try:
        user_id, user_password = database_response[0]
        is_valid_password = bcrypt.checkpw(password.encode(), user_password.encode())

        if is_valid_password:
            jwt_token = jwt.encode({'payloads': user_id}, app.config['SECRET_KEY'], algorithm="HS256")
            return Response(json.dumps({'accessToken': jwt_token}), status=200, mimetype='application/json')
        else:
            return Response('Invalid credentials', status=404, mimetype='text/xml')
    except:
        return Response('Invalid credentials', status=500, mimetype='text/xml')


@app.route("/api/v1/auth/register", methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    email, password = request.json['email'], request.json['password']

    count_users_with_this_email = cur.execute(f"""SELECT * FROM `database`.`persons` WHERE email = '{email}'""")
    if count_users_with_this_email == 0:
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        generated_user_id = str(uuid.uuid4())
        cur.execute(f"""INSERT INTO `database`.`persons` (`ID`, `Email`, `Password`) 
            VALUES ("{generated_user_id}", "{email}", "{hash_password}");""")
        mysql.connection.commit()

        jwt_token = jwt.encode({'payloads': generated_user_id}, app.config['SECRET_KEY'], algorithm="HS256")
        return Response(json.dumps({'accessToken': jwt_token}), status=200, mimetype='application/json')
    else:
        return Response('User with this email is already exists', status=500, mimetype='text/xml')


@app.route("/api/v1/surveys/create", methods=['POST'])
def create_test():
    jwt_token = None
    if "Authorization" in request.headers:
        jwt_token = request.headers["Authorization"].split(" ")[1]
    if not jwt_token:
        return Response('Authentication Token is missing!', status=401, mimetype='text/xml')

    owner_id = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=["HS256"])['payloads']

    cur = mysql.connection.cursor()

    count_users_with_this_id = cur.execute(f"""SELECT * FROM `database`.`persons` WHERE ID = '{owner_id}'""")
    if count_users_with_this_id != 1:
        return Response('Not valid authentication token!', status=403, mimetype='text/xml')

    survey_title = request.json['title']
    generated_id = str(uuid.uuid4())
    cur.execute(f"""INSERT INTO `database`.`surveys` (`ID`, `owner_ID`, `title`)
        VALUES ("{generated_id}", "{owner_id}", "{survey_title}");""")
    mysql.connection.commit()
    return Response(json.dumps({'surveyId': generated_id}), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True)



