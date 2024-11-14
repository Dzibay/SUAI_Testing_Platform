from flask import Flask, request, Response
from flask_mysqldb import MySQL
import json
import bcrypt

app = Flask(__name__)

# Required
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "database"

mysql = MySQL(app)


@app.route("/login", methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    email, password = request.json['email'], request.json['password']
    cur.execute(f"""SELECT password FROM persons where email = '{email}'""")
    database_response = cur.fetchall()
    try:
        user_password = database_response[0][0]
        is_valid_password = bcrypt.checkpw(password.encode(), user_password.encode())
        if is_valid_password:
            return Response('Success', status=200, mimetype='text/xml')
        else:
            return Response('Invalid credentials', status=404, mimetype='text/xml')
    except:
        return Response('Invalid credentials', status=500, mimetype='text/xml')


@app.route("/register", methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    email, password = request.json['email'], request.json['password']
    count_users_with_this_email = cur.execute(f"""SELECT * FROM `database`.`persons` WHERE email = '{email}'""")
    if count_users_with_this_email == 0:
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute(f"""INSERT INTO `database`.`persons` (`Email`, `Password`) VALUES ("{email}", "{hash_password}");""")
        mysql.connection.commit()
        return Response('Register successfully', status=200, mimetype='text/xml')
    else:
        return Response('User with this email is already exists', status=500, mimetype='text/xml')


if __name__ == "__main__":
    app.run(debug=True)



