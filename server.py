from flask import Flask, flash, render_template, request, redirect, session
from mysqlconnection import MySQLConnector
import bcrypt
import re
app = Flask(__name__)
app.secret_key='bullshittysecretkey'
mysql=MySQLConnector('loginandregister')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

def show(param):
	if EMAIL_REGEX.match(param):
		query = "SELECT * FROM users WHERE email = '{}'".format(param)
		print query
		user=mysql.fetch(query)
		return user
	return []

def create(param):
	password_hash = bcrypt.hashpw(str(param['password']), bcrypt.gensalt())
	query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(param['first_name'], param['last_name'], param['email'], password_hash)
	mysql.run_mysql_query(query)
	query_result = show(param['email'])
	if len(query_result) == 1:
		return query_result
	return []

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	current_user = show(request.form['email'])
	if len(current_user) == 1 and bcrypt.hashpw(str(request.form['password']), current_user[0]['password_hash']) == current_user[0]['password_hash']:
		session['user'] = current_user[0]
		return render_template('wall.html')
	query = "SELECT * FROM users JOIN messages ON users.id = messages.user_id"
	mysql.run_mysql_query(query)
	return ('/')

@app.route('/register', methods=['POST'])
def register():
	current_user = show(request.form['email'])
	if len(current_user) > 0:
		return redirect('/')
	user = create(request.form)
	if len(request.form['email']) < 1 or len(request.form['first_name']) < 1 or len(request.form['last_name']) < 1 or len(request.form['password']) < 1 or len(request.form['confirmpass']) < 1:
		flash('Please fill out all fields!')
	elif len(request.form['password']) < 8 or len(request.form['confirmpass']) < 8:
		flash('Password ust be 8 characters or longer!')
	elif not EMAIL_REGEX.match(request.form['email']):
		flash('Invalid email address!')
	elif not request.form['first_name'].isalpha() or not request.form['last_name'].isalpha():
		flash('Name cannot contain numbers!')
	elif len(user) > 0:
		session['user'] = user[0]
		print session['user']
		return render_template('wall.html')
	# return redirect('/')

@app.route('/postmessage', methods=['POST'])
def newmsg():
	message = request.form['newpost']
	query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(session['user']['id'], request.form['newpost'])
	# print 'WORK PLs'
	mysql.run_mysql_query(query)
	return render_template('wall.html')

@app.route('/postcomment', methods=['POST'])
def newcmt():
	session['comment'] = request.form['newcmt']
	query = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(session['user']['id'], message['id'], request.form['newcmt'])
	query2 = "SELECT * FROM messages JOIN comments ON messages.id = comments.message_id"
	mysql.run_mysql_query(query)
	return render_template('wall.html')

app.run(debug=True)