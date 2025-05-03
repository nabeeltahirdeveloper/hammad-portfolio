from flask import Flask, render_template,redirect, request, url_for, flash, session
import datetime
from flask_mysqldb import MySQL
import requests
import json
import hashlib
from flask.cli import with_appcontext
import click




app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'portfoliodb'
app.config['MYSQL_UNIX_SOCKET'] = '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


mysql = MySQL(app)

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database tables if they don't exist
def initialize_db():
    cursor = mysql.connection.cursor()
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL,
            status ENUM('pending', 'approved') DEFAULT 'pending',
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if there's at least one admin user, create a default one if not
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        default_admin_email = 'hammad.qadeer64gb@gmail.com'
        default_admin_password = hash_password('123456')
        cursor.execute(
            "INSERT INTO users (email, password, name, status, is_admin) VALUES (%s, %s, %s, 'approved', TRUE)",
            (default_admin_email, default_admin_password, 'Admin')
        )
    
    mysql.connection.commit()
    cursor.close()

# Register a CLI command to initialize the database
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database tables."""
    initialize_db()
    click.echo('Initialized the database.')

# Add the command to the Flask CLI
app.cli.add_command(init_db_command)

# Run initialization on startup
with app.app_context():
    initialize_db()


@app.route('/')
def home():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    cursor.execute("SELECT * FROM pages")
    pages = cursor.fetchall()

    cursor.execute("SELECT * FROM skills")  
    skills = cursor.fetchall()

    firstSkill = skills[0]

    cursor.execute("SELECT * FROM about_me")
    about_me = cursor.fetchall()

    cursor.close()

    firstAboutMe = about_me[0]









    return render_template('home.html', projects=projects, skills=firstSkill, about_me=firstAboutMe, pages=pages)


@app.route('/admin-login')
def admin_login():
    return render_template('login.html')

@app.route('/admin-signup')
def admin_signup():
    return render_template('signup.html')

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
        return redirect(url_for('home'))

        
    return redirect(url_for('home'))


@app.route('/signup-user', methods=['POST'])
def signup_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Check if email already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            flash('Email already registered. Please login instead.')
            return redirect(url_for('admin_login'))
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (email, password, name, status) VALUES (%s, %s, %s, 'pending')",
            (email, hashed_password, name)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash('Registration successful! Please wait for admin approval.')
        return redirect(url_for('admin_login'))
    
    return redirect(url_for('admin_signup'))


@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        # Fetch form data
        email = request.form['email']
        password = request.form['password']
        
        # Hash the provided password for comparison
        hashed_password = hash_password(password)
        
        # Check user in database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        
        if user and user[4] == 'approved':  # Check if user exists and is approved
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['user_email'] = user[1]
            session['is_admin'] = user[5]
            
            return redirect(url_for('admin'))
        else:
            flash('Invalid login credentials or your account is pending approval.')
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

    cursor.execute("SELECT * FROM pages")
    pages = cursor.fetchall()

    cursor.execute("SELECT * FROM skills")  
    skills = cursor.fetchall()

    firstSkill = skills[0]

    cursor.execute("SELECT * FROM about_me")
    about_me = cursor.fetchall()

    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    
    # Get pending users for approval
    cursor.execute("SELECT * FROM users WHERE status = 'pending'")
    pending_users = cursor.fetchall()
    
    # Get all admin users
    cursor.execute("SELECT * FROM users WHERE status = 'approved'")
    approved_users = cursor.fetchall()

    cursor.close()

    firstAboutMe = about_me[0]

    print("firstAboutMe: ", firstAboutMe)


    return render_template('admin.html', projects=projects, skills=firstSkill, about_me=firstAboutMe, 
                           messages=messages, pages=pages, pending_users=pending_users, 
                           approved_users=approved_users)


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

@app.route('/admin/pages', methods=['GET', 'POST'])
def pages_admin():
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        image = request.form['image']
        title = request.form['title']
        description = request.form['description']
        page_id = request.form.get('page_id')  # This will be None for new pages

        cursor = mysql.connection.cursor()
        if page_id:  # Update existing page
            cursor.execute("UPDATE pages SET name = %s, image = %s, title = %s, description = %s WHERE id = %s",
                         (name, image, title, description, page_id))
        else:  # Create new page
            cursor.execute("INSERT INTO pages (name, image, title, description) VALUES (%s, %s, %s, %s)",
                         (name, image, title, description))
        
        mysql.connection.commit()
        cursor.close()
        flash('Page saved successfully!')
        return redirect(url_for('admin'))

    return render_template('admin.html')

@app.route('/admin/pages/<int:id>/edit', methods=['GET', 'POST'])
def edit_page(id):
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pages WHERE id = %s", (id,))
    page = cursor.fetchone()
    
    # Fetch all required data for the admin template
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    cursor.execute("SELECT * FROM pages")
    pages = cursor.fetchall()

    cursor.execute("SELECT * FROM skills")  
    skills = cursor.fetchall()
    firstSkill = skills[0]

    cursor.execute("SELECT * FROM about_me")
    about_me = cursor.fetchall()
    firstAboutMe = about_me[0]

    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE status = 'pending'")
    pending_users = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE status = 'approved'")
    approved_users = cursor.fetchall()

    cursor.close()
    
    if not page:
        flash('Page not found!')
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        name = request.form['name']
        image = request.form['image']
        title = request.form['title']
        description = request.form['description']
        
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE pages SET name = %s, image = %s, title = %s, description = %s WHERE id = %s",
                      (name, image, title, description, id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Page updated successfully!')
        return redirect(url_for('admin'))
    
    return render_template('admin.html', 
                         edit_page=page,
                         projects=projects,
                         skills=firstSkill,
                         about_me=firstAboutMe,
                         messages=messages,
                         pages=pages,
                         pending_users=pending_users,
                         approved_users=approved_users)

@app.route('/page/<string:page_name>')
def view_page(page_name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pages WHERE name = %s", (page_name,))
    page = cursor.fetchone()
    cursor.close()
    
    if not page:
        flash('Page not found!')
        return redirect(url_for('home'))
    
    return render_template('page.html', page=page)

@app.route("/admin/projects/<int:id>/delete", methods=['GET', 'POST'])
def delete_project(id):
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM projects WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('admin'))

@app.route("/admin/pages/<int:id>/delete", methods=['GET', 'POST'])
def delete_pages(id):
    if 'logged_in' not in session:
        return redirect(url_for('login_user'))
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pages WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('admin'))

@app.route('/admin/users/<int:id>/approve', methods=['GET', 'POST'])
def approve_user(id):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('You need admin privileges to approve users')
        return redirect(url_for('admin'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET status = 'approved' WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('User approved successfully')
    return redirect(url_for('admin'))

@app.route('/admin/users/<int:id>/delete', methods=['GET', 'POST'])
def delete_user(id):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('You need admin privileges to delete users')
        return redirect(url_for('admin'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('User deleted successfully')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)