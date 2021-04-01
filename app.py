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

# The initial page that is loaded upon first accessing the application


@app.route('/')
def index():
    if 'username' in session:
        return render_template(
            'search.html',
            patients=mongo.db.patients.find())

    return render_template('login.html')

# Core Login functionality. Checks password matches the username.  Stored
# in DB the under the users collection


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            # if the user is correct it renders the base page which allows
            # users to search
            if bcrypt.hashpw(
                    request.form['password'].encode('utf-8'),
                    login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return render_template(
                    'search.html', patients=mongo.db.patients.find().sort(
                        "_id", -1))

        return 'Invalid username/password combination'

    else:
        # otherwise this returns the login page.
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')

# Kills the session and renders the login page.


@app.route('/logout')
def logout():
    session['username'] = None
    return render_template('login.html')


# Allows users to search for patients.  Done via mongoDB indexing.
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    patients = list(mongo.db.patients.find({"$text": {"$search": query}}))
    return render_template("search.html", patients=patients)

# Enables the logged in user to create a new patient.  Stores this in the
# DB under the collection Patients


@app.route('/new', methods=['POST', 'GET'])
def new_patient():
    if request.method == 'POST':
        pid = uuid.uuid4().hex.upper()
        mongo.db.patients.insert_one(
            {
                'patient_id': pid,
                'first_name': request.form['first_name'],
                'surname': request.form['surname'],
                'email': request.form['email'],
                'phone_number': request.form['phone_number'],
                'AddressLine1': request.form['AddressLine1'],
                'AddressLine2': request.form['AddressLine2'],
                'Town': request.form['Town'],
                'postcode': request.form['postcode'],
                'gender': request.form['gender'],
                'dob': request.form['dob'],
                'blood_type': request.form['blood_type'],
                'ethnicity': request.form['ethnicity'],
                'smoking_habits': request.form['smoking_habits'],
                'drinking_habits': request.form['drinking_habits'],
                'exercise_frequency': request.form['exercise_frequency'],
                'allergies': request.form['allergies'],
                'conditions': request.form['conditions'],
            })
        this_patient = mongo.db.patients.find_one({"patient_id": pid})
        return render_template('dashboard.html', patient=this_patient)

    return render_template('new-patient.html')


# Renders the unique patients dashboard.
@app.route('/dashboard/<patient_id>', methods=['POST', 'GET'])
def dashboard(patient_id):
    if request.method == 'GET':
        this_patient = mongo.db.patients.find_one(
            {"_id": ObjectId(patient_id)})
        return render_template('dashboard.html', patient=this_patient)
    return redirect(url_for('index'))

# Renders the unique patients profile which displays their personal information


@app.route('/profile/<patient_id>', methods=['POST', 'GET'])
def profile(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('profile.html', patient=this_patient)

# INCOMPLETE - PLAN IS TO STORE INFORMATION IN A DB COLLECTION LINKED BY
# USERS ._ID AND SHOW THEIR HISTORY.


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/medication/<patient_id>')
def medication(patient_id):
    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    return render_template(
        'medication.html',
        medications=meds,
        patient=patient)


@app.route('/newmeds/<patient_id>', methods=['POST', 'GET'])
def new_medicine(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    if request.method == 'POST':
        mongo.db.medication.insert_one(
            {
                'patient_id': request.form['id'],
                'medication_name': request.form['medication_name'],
                'dosage': request.form['dosage'],
                'start': request.form['start'],
                'end': request.form['end'],
                'amount': request.form['amount'],
                'morning': request.form['morning'],
                'afternoon': request.form['afternoon'],
                'evening': request.form['evening'],
                'notes': request.form['notes'],
                'complete': False
            })
        meds = list(mongo.db.medication.find())
        return render_template(
            'medication.html',
            medications=meds,
            patient=this_patient)

    return render_template('new-medication.html', patient=this_patient)


@app.route('/updated/<patient_id>/<medication_id>', methods=['POST'])
def edit_medication(medication_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    medication = mongo.db.medication
    medication.update({'_id': ObjectId(medication_id)},
    {
        'patient_id': request.form['id'],
        'medication_name': request.form['medication_name'],
        'dosage': request.form['dosage'],
        'start': request.form['start'],
        'end': request.form['end'],
        'amount': request.form['amount'],
        'morning': request.form['morning'],
        'afternoon': request.form['afternoon'],
        'evening': request.form['evening'],
        'notes': request.form['notes'],
        'complete': False
    })
    return render_template(
        'medication.html',
        medications=meds,
        patient=this_patient)


@app.route('/delete/<patient_id>/<medication_id>')
def delete_medication(medication_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    mongo.db.medication.remove({'_id': ObjectId(medication_id)})
    return render_template(
        'medication.html',
        medications=meds,
        patient=this_patient)


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
