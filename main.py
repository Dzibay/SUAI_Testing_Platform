from flask import Flask, request
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

# Required
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "database"

mysql = MySQL(app)


@app.route("/login", methods=['GET'])
def login():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM persons""")
    rv = cur.fetchall()
    return json.dumps(rv)


@app.route("/register", methods=['POST'])
def register():
    email, password = request.form['email'], request.form['password']
    cur = mysql.connection.cursor()
    cur.execute(f"""INSERT INTO `database`.`persons` (`Email`, `Password`) VALUES ('{email}', '{password}');""")
    mysql.connection.commit()
    return 'Succes'


if __name__ == "__main__":
    app.run(debug=True)


