# app/views.py
from app import app
from flask import render_template, flash, redirect, url_for, session, request, logging

from flask_mysqldb import MySQL

from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField, HiddenField
from passlib.hash import sha256_crypt
from functools import wraps
from data import Articles
from flask import render_template
from data import *

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Autonoma123*'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# INIT MYSQL
mysql = MySQL(app)

data = Articles()
app.secret_key = "secrect123"


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


class Add_article(Form):
    title = StringField('Title')
    author = StringField('Author')
    date = DateField('Date')


class Edit_article(Form):
    id = HiddenField('id')
    title = StringField('Title')
    author = StringField('Author')
    date = DateField('Date')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from articles")
    articles = cur.fetchall()
    print(articles)
    return render_template("articles.html", articles=articles)


@app.route('/articles/<variable>', methods=['GET'])
def article(variable):
    # do your code here
    article = data[int(variable)]
    return render_template("article.html", para1=article)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create Cursor
        cur = mysql.connection.cursor()
        # Execute Query
        cur.execute("INSERT INTO users(name, email,username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute(
            "SELECT * FROM users WHERE username =%s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['id'] = data['id']
                flash('You are logged in', 'success')
                app.logger.info('PASSWORD MATCHED')
                return redirect(url_for('dashboard'))

            else:
                app.logger.info('PASSWORD NO MATCHED')
                error = 'Invalid login'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()

        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Plese login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@is_logged_in
@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT a.id, u.name as 'author', a.title, a.date FROM articles a INNER JOIN users u ON u.id=a.author WHERE u.id = 1")
    articles = cur.fetchall()
    return render_template('dashboard.html', articles=articles)


@app.route('/delete_article/<id>', methods=['POST'])
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id =%s", [id])
    mysql.connection.commit()
    flash('Article deleted', 'danger')
    return dashboard()


@is_logged_in
@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    form = Add_article(request.form)
    # print(session['id'])
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles VALUES (null,%s,%s,%s)",
                    (session['id'], request.form['title'], request.form['date']))
        response = cur.fetchall()
        mysql.connection.commit()
        flash('Article addded', 'success')
    return render_template('add_article.html', form=form)


@is_logged_in
@app.route('/edit_article/<id>', methods=['GET', 'POST'])
def edit_article(id):
    form = Edit_article(request.form)
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM articles where id = "+str(id))
        article = cur.fetchall()
        print(article[0])
        return render_template('edit_article.html', article=article[0])
    else:
        # print(request.form['id']) 
        cur = mysql.connection.cursor()
        cur.execute("UPDATE articles SET title=%s, date=%s WHERE id =%s",(request.form['title'],request.form['date'],int(request.form['id'])))
        mysql.connection.commit()
        flash("Article edited succesfully", "success")
        return redirect(url_for('dashboard'))


