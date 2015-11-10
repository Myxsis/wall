from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
app = Flask(__name__)
app.secret_key='thebestsecretkeyhahaha'
mysql = MySQLConnector('')

def show(param):
	if EMAIL_REGEX.match(param):
		query = "SELECT * FROM users where email = '{}'".format(param)
		print query
		user=mysql.fetch(query)
		return user
	return []

def create(param):
	password_hash = bcrypt.hashpw(str(param['password']), bcrypt.gensalt())
	query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(param['first_name'], param['last_name'], param['email'], password_hash)
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
	if len(current_user) == 1 and bcrypt.hash(str(request.form['password']), current_user[0]['password_hash']) == current_user[0]['password_hash']:
		session['user'] = current_user[0]
		return render_template('success.html')
	return ('/')

@app.route('/register', methods=['POST'])
def register():
	current_user = show(request.form['email'])
	user = create(request.form)
	if len(current_user) > 0:
		return redirect('/')
	if len(request.form['email']) < 1 or len(request.form['first_name']) < 1 or len(request.form['last_name']) < 1 or len(request.form['password']) < 1 or len(request.form['confirmpass']) < 1:
		flash('Please fill out all fields!')
	elif len(request.form['password']) < 8 or len(request.form['confirmpass']) < 8:
		flash('Password must be 8 characters or longer!')
	elif not EMAIL_REGEX.match(request.form['email']):
		flash('Invalid email address!')
	elif session['fname'].isalpha() == False or session['lname'].isalpha() == False:
		flash('Name cannot contain numbers!')
	elif request.form['confirmpass'] != request.form['password']:
		flash('Passwords do not match!')
	elif len(user) > 0:
		session['user'] = user[0]
		print session['user']
		return render_template('success.html')

app.run(debug=True)