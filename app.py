

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)


app.secret_key = 'T5$T@123#' 
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'stockmarket'

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg, username=session['username'])
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT users.username, posts.content, posts.created_at FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC')
    posts = cursor.fetchall()

    print(posts)  # Add this line to print posts in the console

    if 'loggedin' in session:
        if request.method == 'POST' and 'content' in request.form:
            content = request.form['content']
            user_id = session['id']
            cursor.execute('INSERT INTO posts (user_id, content) VALUES (%s, %s)', (user_id, content))
            mysql.connection.commit()
            # After posting, redirect to the posts page to see the updated list
            return redirect(url_for('posts'))

    return render_template('posts.html', username=session.get('username'), posts=posts)



@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'loggedin' in session:
        if request.method == 'POST' and 'content' in request.form:
            content = request.form['content']
            user_id = session['id']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO posts (user_id, content) VALUES (%s, %s)', (user_id, content))
            mysql.connection.commit()
            return redirect(url_for('posts'))
    return render_template('new_post.html', username=session.get('username'))



if __name__ == "__main__":
    app.run(debug=True)
