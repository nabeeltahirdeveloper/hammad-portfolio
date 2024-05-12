from flask import Flask, render_template,redirect, request, url_for, flash, session
import datetime
from flask_mysqldb import MySQL
import requests
import json




app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'flask_blog'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


mysql = MySQL(app)


@app.route('/')
def home():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    cursor.execute("SELECT * FROM skills")  
    skills = cursor.fetchall()

    firstSkill = skills[0]

    cursor.execute("SELECT * FROM about_me")
    about_me = cursor.fetchall()

    cursor.close()

    firstAboutMe = about_me[0]









    return render_template('home.html', projects=projects, skills=firstSkill, about_me=firstAboutMe)


@app.route('/admin-login')
def admin_login():
    return render_template('login.html')

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


@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        print("Name: ", name)
        print("Email: ", email)
        print("Subject: ", subject)
        print("Message: ", message)

        url = "https://api.emailjs.com/api/v1.0/email/send"

        payload = json.dumps({
        "service_id": "service_57ost48",
        "template_id": "template_vhigtna",
        "user_id": "GBUhGMkiuAlFPey9W",
        "accessToken": "a5WW1KshbNj7z1EVJSeDr",
        "template_params": {
            "subject": subject,
            "message": message,
            "user_email": email,
            "from_name": name,
        }
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


        # Insert form data into database
        cursor = mysql.connection.cursor()
        cursor.execute(f"INSERT INTO messages (name, email, subject, message) VALUES ('{name}', '{email}', '{subject}', '{message}')")
        mysql.connection.commit()
        cursor.close()

        # Redirect to blog page or some other page after posting
        return render_template('home.html')

    return render_template('home.html')


@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        # Fetch form data
        email = request.form['email']
        password = request.form['password']

        print("Email: ", email)
        print("Password: ", password)

        if email == 'hammad.qadeer64gb@gmail.com' and password == '123456':
            session['logged_in'] = True


            return redirect(url_for('admin'))

        else:

            return render_template('login.html')

    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
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
    

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    cursor.execute("SELECT * FROM skills")  
    skills = cursor.fetchall()

    firstSkill = skills[0]

    cursor.execute("SELECT * FROM about_me")
    about_me = cursor.fetchall()

    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()


    cursor.close()

    firstAboutMe = about_me[0]

    print("firstAboutMe: ", firstAboutMe)


    return render_template('admin.html', projects=projects, skills=firstSkill, about_me=firstAboutMe, messages=messages)


@app.route('/admin/about', methods=['GET', 'POST'])
def about_admin():
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    if request.method == 'POST':
        # Fetch form data
        profile = request.form['profile']
        description = request.form['description']

        # Insert form data into database
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE about_me SET pic = %s, description = %s", (profile, description))
        mysql.connection.commit()
        cursor.close()

        # Redirect to blog page or some other page after posting
        return redirect(url_for('admin'))

    return render_template('admin.html')


@app.route('/admin/skills', methods=['GET', 'POST'])
def skills_admin():
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    if request.method == 'POST':
        # Fetch form data
        skill = request.form['skill']
        htmlLevel = request.form['htmlLevel']
        cssLevel = request.form['cssLevel']
        jsLevel = request.form['jsLevel']
        adobeLevel = request.form['adobeLevel']
        corelLevel = request.form['corelLevel']
        wordpressLevel = request.form['wordpressLevel']

        # Update form data into database
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE skills SET description = %s, html = %s, css = %s, javascript = %s, adobe = %s, corel = %s, wordpress = %s", (skill, htmlLevel, cssLevel, jsLevel, adobeLevel, corelLevel, wordpressLevel))

        mysql.connection.commit()
        cursor.close()


        # Redirect to blog page or some other page after posting
        return redirect(url_for('admin'))

    return render_template('admin.html')


@app.route('/admin/projects', methods=['GET', 'POST'])
def projects_admin():
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    if request.method == 'POST':
        # Fetch form data
        profilePic = request.form['profilePic']
        title = request.form['title']
        description = request.form['description']

        # Insert form data into database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO projects (profile_pic, title, description) VALUES (%s, %s, %s)", (profilePic, title, description))
        mysql.connection.commit()
        cursor.close()

        # Redirect to blog page or some other page after posting
        return redirect(url_for('admin'))

    return render_template('admin.html')


@app.route("/admin/projects/<int:id>/delete", methods=['GET', 'POST'])
def delete_project(id):
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM projects WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)