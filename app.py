import os
import json
import uuid
from flask import Flask, render_template, session, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
from datetime import datetime as date
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


@app.route("/search-med/<patient_id>", methods=["GET", "POST"])
def search_med(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    query = request.form.get("query")
    meds = list(mongo.db.medication.find({"$text": {"$search": query}}))
    return render_template("medication.html", patient=this_patient, medications=meds)


# Enables the logged in user to create a new patient.  Stores this in the
# DB under the collection Patients
@app.route('/new', methods=['POST', 'GET'])
def new_patient():
    if request.method == 'POST':
        pid = 1
        col = mongo.db.patients
        for doc in col.find():
            pid = pid+1
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
    return render_template('profile.html', patient=this_patient,consultations=mongo.db.consultations.find())

# INCOMPLETE - PLAN IS TO STORE INFORMATION IN A DB COLLECTION LINKED BY
# USERS ._ID AND SHOW THEIR HISTORY.
@app.route('/smartform/<patient_id>', methods=['POST', 'GET'])
def smart_form(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('smart_form.html', patient=this_patient,consultations=mongo.db.consultations.find())

@app.route('/edit-patient/<patient_id>', methods=['POST', 'GET'])
def edit_patient(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('update-personal-info.html', patient=this_patient,consultations=mongo.db.consultations.find())

@app.route('/update-patient/<patient_id>', methods=['POST', 'GET' ])
def update_medical(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    patients = mongo.db.patients
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"blood_type":request.form.get('blood_type')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"smoking_habits":request.form.get('smoking_habits')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"drinking_habits":request.form.get('drinking_habits')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"exercise_frequency":request.form.get('exercise_frequency')}})
    return render_template('profile.html', patient=this_patient,consultations=mongo.db.consultations.find())

@app.route('/edit-medical/<patient_id>', methods=['POST', 'GET'])
def edit_patient_med(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('update-med-info.html', patient=this_patient,consultations=mongo.db.consultations.find())


@app.route('/update-medical/<patient_id>', methods=['POST', 'GET' ])
def update_patient(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    patients = mongo.db.patients
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"first_name":request.form.get('first')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"surname":request.form.get('last')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"dob":request.form.get('dob')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"gender":request.form.get('gender')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"ethnicity":request.form.get('ethnicity')}})
    return render_template('profile.html', patient=this_patient,consultations=mongo.db.consultations.find())


@app.route('/edit-allergy/<patient_id>', methods=['POST', 'GET'])
def edit_patient_allergy(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('update-allergy-info.html', patient=this_patient,consultations=mongo.db.consultations.find())


@app.route('/update-allergy/<patient_id>', methods=['POST', 'GET' ])
def update_allergy(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    patients = mongo.db.patients
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"allergies":request.form.get('allergies')}})
    patients.update({"_id": ObjectId(patient_id)}, { "$set": {"conditions":request.form.get('conditions')}})
    return render_template('profile.html', patient=this_patient,consultations=mongo.db.consultations.find())


@app.route('/medication/<patient_id>')
def medication(patient_id):
    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    return render_template(
        'medication.html',
        medications=meds,
        patient=patient)

@app.route('/current-medication/<patient_id>')
def current_medication(patient_id):
    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    today = date.today()
    d3 = today.strftime("%Y-%m-%d")
    print(d3)
    meds = list(mongo.db.medication.find({"end": {"$gte": d3},"start": {"$lte": d3}}))
    return render_template(
        'current_medication.html',
        medications=meds,
        patient=patient)

@app.route('/past-medication/<patient_id>')
def past_medication(patient_id):
    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    today = date.today()
    d3 = today.strftime("%Y-%m-%d")
    print(d3)
    meds = list(mongo.db.medication.find( { "end": { "$lt":d3 } } ))
    return render_template(
        'past_medication.html',
        medications=meds,
        patient=patient)



@app.route('/newmeds/<patient_id>', methods=['POST', 'GET'])
def new_medicine(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    if request.method == 'POST':
        mongo.db.medication.insert_one(
            {
                'patient_id': request.form['id'],
                'medication_name': request.form['medication_name'],
                'Route': request.form['Route'],
                'start': request.form['start'],
                'end': request.form['end'],
                'dosage': request.form['dosage'],
                'complete': False
            })
        return render_template(
            'medication.html',
            medications=meds,
            patient=this_patient)

    return render_template('new-medication.html', patient=this_patient, medications=meds)


@app.route('/edit-medication/<patient_id>_<medication_id>', methods=['POST', 'GET'])
def edit_medication(medication_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find({'_id': ObjectId(medication_id)}))
    return render_template('update-medication.html', patient=this_patient, medications=meds)



@app.route('/update/<patient_id>/<medication_id>', methods=['POST'])
def update_medication(medication_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    medication = mongo.db.medication
    medication.update({"_id": ObjectId(medication_id)}, { "$set": {"medication_name":request.form.get('medication_name')}})
    medication.update({"_id": ObjectId(medication_id)}, { "$set": {"Route":request.form.get('Route')}})
    medication.update({"_id": ObjectId(medication_id)}, { "$set": {"start":request.form.get('start')}})
    medication.update({"_id": ObjectId(medication_id)}, { "$set": {"dosage":request.form.get('dosage')}})
    return render_template(
        'medication.html',
        medications=meds,
        patient=this_patient)


@app.route('/delete-medication/<patient_id>_<medication_id>')
def delete_medication(medication_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    meds = list(mongo.db.medication.find())
    mongo.db.medication.remove({'_id': ObjectId(medication_id)})
    return render_template(
        'medication.html',
        medications=meds,
        patient=this_patient)



@app.route('/consulatation/<patient_id>', methods=['POST', 'GET' ])
def new_consulatation(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    if request.method == 'POST':
        mongo.db.consultations.insert_one(
            {
                'patient_id': request.form['id'],
                'consultation_type': "visit",
                'date_of_consultation': request.form['date_of_consultation'],
                'day_of_consultation': date.today().strftime("%A"),
                'physician': request.form['physician'],
                'reason': request.form['reason'],
                'symptoms': request.form['symptoms'],
                'examination': request.form['examination'],
                'allergies': request.form['allergies'],
                'order_blood': request.form['order_blood'],
                'impression': request.form['impression'],
                'treatment': request.form['treatment']

            })
    return render_template('smart_form.html', patient=this_patient,consultations=mongo.db.consultations.find())


@app.route('/smartform-timeline/<patient_id>', methods=['POST', 'GET'])
def gettimeline(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('smart_form_timeline.html', patient=this_patient,consultations=mongo.db.consultations.find())

@app.route('/smartform-surgical/<patient_id>', methods=['POST', 'GET'])
def smart_form_surgical(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('smart_form_surgical.html', patient=this_patient)

@app.route('/smartform-social/<patient_id>', methods=['POST', 'GET'])
def smart_form_social(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('smart_form_social.html', patient=this_patient)

@app.route('/smartform-consultation/<patient_id>', methods=['POST', 'GET'])
def smart_form_consultation(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    return render_template('smart_form_consultation.html', patient=this_patient)


@app.route('/lab-data/<patient_id>', methods=['POST', 'GET'])
def labdata(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    return render_template('labdata.html', patient=this_patient,labdata=data)


@app.route('/lab-data-current/<patient_id>', methods=['POST', 'GET'])
def labdata_current(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    return render_template('labdata_current.html', patient=this_patient,labdata=data)

@app.route('/lab-data-past/<patient_id>', methods=['POST', 'GET'])
def labdata_past(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    return render_template('labdata_past.html', patient=this_patient,labdata=data)

@app.route('/labdata/<patient_id>', methods=['POST', 'GET'])
def new_labdata(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    lid = uuid.uuid4().hex.upper()
    if request.method == 'POST':
        mongo.db.labdata.insert_one(
            {
                'patient_id': request.form['id'],
                'Type': request.form['Type'],
                'Date': request.form['Date'],
                'Status': request.form['Status']
            })
        return render_template('labdata.html', labdata=data, patient=this_patient)

    return render_template('new-labdata.html', patient=this_patient, labdata=data)



@app.route("/search-lab/<patient_id>", methods=["GET", "POST"])
def search_lab(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    query = request.form.get("query")
    data = list(mongo.db.labdata.find({"$text": {"$search": query}}))
    return render_template("labdata.html", patient=this_patient, labdata=data)

@app.route('/edit-labdata/<patient_id>_<labdata_id>', methods=['POST', 'GET'])
def edit_labdata(labdata_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find({'_id': ObjectId(labdata_id)}))
    return render_template('update-labdata.html', patient=this_patient, labdata=data)



@app.route('/update-labdata/<patient_id>/<labdata_id>', methods=['POST'])
def update_labdata(labdata_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    labdata = mongo.db.labdata
    labdata.update({"_id": ObjectId(labdata_id)}, { "$set": {"Type":request.form.get('Type')}})
    labdata.update({"_id": ObjectId(labdata_id)}, { "$set": {"Date":request.form.get('Date')}})
    labdata.update({"_id": ObjectId(labdata_id)}, { "$set": {"Status":request.form.get('Status')}})
    return render_template(
        'labdata.html',
         labdata=data,
        patient=this_patient)


@app.route('/preventative/<patient_id>', methods=['POST', 'GET'])
def preventative(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    preventative = list(mongo.db.preventative.find())
    return render_template('preventative.html', patient=this_patient,preventative=preventative)


@app.route("/search-preventative/<patient_id>", methods=["GET", "POST"])
def search_pre(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    query = request.form.get("query")
    preventative = list(mongo.db.preventative.find({"$text": {"$search": query}}))
    return render_template("preventative.html", patient=this_patient, preventative=preventative)



@app.route('/new-preventative/<patient_id>', methods=['POST', 'GET'])
def new_preventative(patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    preventative = list(mongo.db.preventative.find())
    if request.method == 'POST':
        mongo.db.preventative.insert_one(
            {
                'patient_id': request.form['id'],
                'MedName': request.form['MedName'],
                'Date': request.form['Date'],
                'Type': request.form['Type'],
                'Container': request.form['Container'],
                'State': request.form['State']

            })
        return render_template('preventative.html', preventative=preventative, patient=this_patient)

    return render_template('new-preventative.html', patient=this_patient, preventative=preventative)

@app.route('/edit-preventative/<patient_id>_<preventative_id>', methods=['POST', 'GET'])
def edit_preventative(preventative_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    pre = list(mongo.db.preventative.find({'_id': ObjectId(preventative_id)}))
    return render_template('update-preventative.html', patient=this_patient, preventative=pre)



@app.route('/update-preventative/<patient_id>/<preventative_id>', methods=['POST'])
def update_preventative(preventative_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    pre = list(mongo.db.preventative.find())
    preventative = mongo.db.preventative
    preventative.update({"_id": ObjectId(preventative_id)}, { "$set": {"MedName":request.form.get('MedName')}})
    preventative.update({"_id": ObjectId(preventative_id)}, { "$set": {"Date":request.form.get('Date')}})
    preventative.update({"_id": ObjectId(preventative_id)}, { "$set": {"Type":request.form.get('Type')}})
    preventative.update({"_id": ObjectId(preventative_id)}, { "$set": {"Container":request.form.get('Container')}})
    preventative.update({"_id": ObjectId(preventative_id)}, { "$set": {"State":request.form.get('State')}})
    return render_template(
        'preventative.html',
         preventative=pre,
        patient=this_patient)


@app.route('/delete-labdata/<patient_id>_<preventative_id>')
def delete_labdata(labdata_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    data = list(mongo.db.labdata.find())
    mongo.db.labdata.remove({'_id': ObjectId(labdata_id)})
    return render_template('labdata.html',labdata=data,patient=this_patient)

@app.route('/delete-preventative/<patient_id>_<preventative_id>')
def delete_preventative(preventative_id, patient_id):
    this_patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
    preventative = list(mongo.db.preventative.find())
    mongo.db.preventative.remove({'_id': ObjectId(preventative_id)})
    return render_template('preventative.html',preventative=preventative,patient=this_patient)



if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)


