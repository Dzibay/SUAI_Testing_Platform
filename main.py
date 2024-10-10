from flask import Flask, request
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
    try:
        cur.execute(f"""SELECT password FROM persons where email = '{email}'""")
        rv = cur.fetchall()[0][0]
        result = bcrypt.checkpw(password.encode(), rv.encode())
        return json.dumps(result)
    except:
        return json.dumps(False)


@app.route("/register", methods=['POST'])
def register():
    email, password = request.json['email'], request.json['password']
    hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur = mysql.connection.cursor()
    cur.execute(f"""INSERT INTO `database`.`persons` (`Email`, `Password`) VALUES ("{email}", "{hash_password}");""")
    mysql.connection.commit()
    return 'Succes'


if __name__ == "__main__":
    app.run(debug=True)


