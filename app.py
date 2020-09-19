import os
import json
import uuid
from flask import Flask, render_template, session, request, redirect, url_for
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
    if 'username' in session:
        return render_template('search.html', patients=mongo.db.patients.find())

    return render_template('index.html')


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    patients = list(mongo.db.patients.find({"$text": {"$search": query}}))
    return render_template("search.html", patients=patients)


@app.route('/dashboard/<patient_id>', methods = ['POST', 'GET'])
def dashboard(patient_id):
    if request.method == 'GET':
        this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
        return render_template('dashboard.html', patient=this_patient)
    return redirect(url_for('index'))


@app.route('/new', methods=['POST', 'GET'])
def new_patient():
    if request.method == 'POST':
        id = uuid.uuid4().hex[:8]
        mongo.db.patients.insert(
        {
            'patient_id': id,
            'full_name': request.form['full_name'],
            'email': request.form['email'],
            'phone_number': request.form['phone_number'],
            'AddressLine1': request.form['AddressLine1'],
            'AddressLine2': request.form['AddressLine2'],
            'Town': request.form['Town'],
            'postcode': request.form['postcode'],
            'gender': request.form['gender'],
            'dob': request.form['dob'],
            'blood-type': request.form['blood-type'],
            'ethnicity': request.form['ethnicity'],
            'smoking-habits': request.form['smoking-habits'],
            'drinking-habits': request.form['drinking-habits'],
            'exercise-frequency': request.form['exercise-frequency'],
            'allergies': request.form['allergies'],
            'conditions': request.form['conditions'],
            })
    return render_template('new-patient.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return render_template('dashboard.html')

        return 'Invalid username/password combination'

    else:
        return render_template('index.html')


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


@app.route('/logout')
def logout():
    session['username'] = None
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/medication')
def medication():
    return render_template('medication.html')


@app.route('/symptoms')
def symptoms():
    return render_template('symptoms.html')


@app.route('/care-plan')
def care_plan():
    return render_template('care-plan.html')


@app.route('/tests')
def tests():
    return render_template('tests.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
