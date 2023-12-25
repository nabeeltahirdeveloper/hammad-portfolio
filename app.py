from flask import Flask, render_template,redirect, request, url_for
import datetime
from flask_mysqldb import MySQL
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'flask_blog'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM posts")  # Assuming your table is named 'posts'
    posts = cursor.fetchall()
    cursor.close()
    return render_template('blog.html', posts=posts)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Fetch form data
        title = request.form['title']
        content = request.form['content']
        date_posted = datetime.datetime.now()

        # Insert form data into database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO posts (title, content, date_posted) VALUES (%s, %s, %s)", (title, content, date_posted))
        mysql.connection.commit()
        cursor.close()

        # Redirect to blog page or some other page after posting
        return redirect(url_for('blog'))

    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)