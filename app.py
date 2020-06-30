import os
import json
from flask import Flask, render_template, session, request, redirect
from flask import url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
import bcrypt

if path.exists("env.py"):
    import env

app = Flask(__name__)

# Defining variables database and MongoDB url
app.config["MONGO_DBNAME"] = os.getenv('MONGO_DBNAME')
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
def index():
    # if 'username' in session:
    # return 'You are logged in as ' + session['username']

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return render_template('dashboard.html')

    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
