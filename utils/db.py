from flask_mysqldb import MySQL

def create_tables(app, mysql):
    with app.app_context():
        cur = mysql.connection.cursor()
        # Create persons table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                ID VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        # Create surveys table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                ID VARCHAR(36) PRIMARY KEY,
                owner_ID VARCHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                status VARCHAR(50) NOT NULL,
                FOREIGN KEY (owner_ID) REFERENCES persons(ID)
            )
        """)
        # Create questions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                ID VARCHAR(36) PRIMARY KEY,
                survey_ID VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                `order` INT(50) NOT NULL,
                type VARCHAR(50) NOT NULL,
                FOREIGN KEY (survey_ID) REFERENCES surveys(ID) ON DELETE CASCADE
            )
        """)
        # Create answers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                ID VARCHAR(36) PRIMARY KEY,
                question_ID VARCHAR(36) NOT NULL,
                text VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                FOREIGN KEY (question_ID) REFERENCES questions(ID) ON DELETE CASCADE
            )
        """)
        mysql.connection.commit()
        cur.close()
