from flask import Flask
from flask_mysqldb import MySQL
import yaml
import MySQLdb

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# Temporarily remove database name for initial connection
# app.config['MYSQL_DB'] = 'portfoliodb'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

def create_database():
    # Create a direct connection without database
    conn = MySQLdb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        unix_socket=app.config['MYSQL_UNIX_SOCKET']
    )
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS portfoliodb")
    conn.commit()
    cursor.close()
    conn.close()

# Initialize MySQL after database creation
app.config['MYSQL_DB'] = 'portfoliodb'  # Add database name back
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            image VARCHAR(255),
            title VARCHAR(255),
            description TEXT
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
        create_database()  # Create database first
        create_and_populate_tables()  # Then create and populate tables
