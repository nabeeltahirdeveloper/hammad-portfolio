from flask import Flask
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'flask_blog'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
mysql = MySQL(app)

def create_and_populate_tables():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            profile_pic VARCHAR(255)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            description TEXT,
            html INT,
            css INT,
            javascript INT,
            adobe INT,
            corel INT,
            wordpress INT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS about_me (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pic VARCHAR(255),
            description TEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            subject VARCHAR(255),
            message TEXT
        
        );
    ''')

    # Insert dummy data if table is empty
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO projects (title, description, profile_pic) VALUES ('Sample Project', 'This is a sample project description.', 'path/to/image.jpg')")
    
    cursor.execute("SELECT COUNT(*) FROM skills")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO skills (description, html, css, javascript, adobe, corel, wordpress) VALUES ('Sample Skill', 80, 70, 60, 50, 40, 30)")
    
    cursor.execute("SELECT COUNT(*) FROM about_me")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO about_me (pic, description) VALUES ('path/to/profile.jpg', 'This is a sample about me description.')")
    
    mysql.connection.commit()
    cursor.close()

if __name__ == '__main__':
    with app.app_context():
        create_and_populate_tables()
