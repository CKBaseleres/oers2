from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, validators, BooleanField, IntegerField, widgets, SelectMultipleField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField, TimeRange
from datetime import time
from passlib.hash import sha256_crypt
import datetime
from functools import wraps
import sys
import os

app = Flask(__name__, static_url_path="/static", static_folder="static")

# MySql Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'capstone'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySql
mysql = MySQL(app)



# global equip
# global fac
# equip = []
# fac = []
# cur = mysql.connection.cursor()
# # GET DATA FROM DATABASE FOR EQUIPMENTS
# cur.execute("SELECT * FROM equipment")
# result = cur.fetchall()
# for res in result:
#     equip.append(res["equipmentName"])
#     # GET DATA FROM DATABASE FOR FACILITIES
# cur.execute("SELECT * FROM facility")
# re = cur.fetchall()
# for r in re:
#     fac.append(r["facilityName"])

# Checks Session
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Log In','danger')
            return redirect(url_for('login'))
    return wrap

# Student Registration Form
class StudentRegisterForm(FlaskForm):
    def validate_studentNumber(form,field):
        if len(field.data) > 15 or len(field.data) < 15:
            raise ValueError('Student Number must be 15 characters long.')
    studentNumber = StringField('',[],
        render_kw={
            "placeholder": "Student Number",
            "class": "form-control"
            })
    firstName = StringField('', [validators.length(min=1, max=50)],
        render_kw={
            "placeholder": "First Name",
            "class": "form-control"
            })
    lastName = StringField('', [validators.length(min=1, max=50)],\
        render_kw={
            "placeholder": "Last Name",
            "class": "form-control"
            })
    email = StringField('', [
        validators.length(min=6,max=50),
        validators.email(message='Invalid e-mail')
    ],  render_kw={
            "placeholder": "E-mail",
            "class": "form-control"
            })
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match.')
    ],  render_kw={
            "placeholder": "Password",
            "class": "form-control"
            })
    confirm = PasswordField('',
        render_kw={
            "placeholder": "Confirm Password",
            "class": "form-control"})

class AddEquipmentForm(FlaskForm):
    equipmentPropertyNumber = StringField('Property Number',
        [validators.length(min=5, max=50)],
        render_kw={
            "class": "form-control"
            })
    equipmentName = StringField('Equipment Name',
        [validators.length(min=1, max=50)],
        render_kw={
            "class": "form-control"
        })
    quantity = IntegerField('Quantity',
        [validators.NumberRange(message='Not a number value.')],
        render_kw={
            "class": "form-control"
        })

class AddFacilityForm(FlaskForm):
    facilityPropertyNumber = StringField('Property Number',
        [validators.length(min=5, max=50)],
        render_kw={
            "class": "form-control"
        })
    facilityName = StringField('Facility Name',
        [validators.length(min=1, max=50)],
        render_kw={
            "class": "form-control"
        })
    availability = SelectField('Availability',
        choices = [('Yes','Yes'),('No','No')],
        render_kw={
            "class": "form-control"
        })

class ReservationForm(FlaskForm):
    checkbox = BooleanField('Agree?',)
    resFrom = DateField('From', format= "%Y-%m-%d", render_kw={"class": "form-control"})
    reseFrom = TimeField('To', format= "%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(17,00)
        )],
         render_kw={"class" : "form-control"})
    resTo = TimeField('To', format="%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(19,00)
        )],
        render_kw={"class" : "form-control"})

@app.route('/add-facility', methods=['POST','GET'])
@is_logged_in
def addfacility():
    form = AddFacilityForm()
    if form.validate_on_submit():
        facilityPropertyNumber = form.facilityPropertyNumber.data
        facilityName = form.facilityName.data
        availability = form.availability.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO facility(facilityPropertyNumber,facilityName,availability) VALUES (%s,%s,%s)",
            (facilityPropertyNumber,facilityName,availability))
        mysql.connection.commit()
        cur.close()

        flash("Facility Added!","success")

        return redirect(url_for('index'))
    return render_template('add_facility.html', form=form)

@app.route('/equipment/dashboard')
@is_logged_in
def EquipmentDashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM equipment")
    equipments = cur.fetchall()

    if result > 0:
        return render_template('equipmentDashboard.html', equipments=equipments)
    else:
        msg = "No Equipments Found."
        return render_template('equipmentDashboard.html', msg=msg)
    return render_template('equipmentDashboard.html')


@app.route('/facility/dashboard')
@is_logged_in
def FacilityDashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM facility")
    facilities = cur.fetchall()

    if result > 0:
        return render_template('facilityDashboard.html', facilities=facilities)
    else:
        msg = "No Facilities Found."
        return render_template('facilityDashboard.html', msg=msg)
    return render_template('facilityDashboard.html')

@app.route('/facility/editFacility/<string:facilityPropertyNumber>', methods=['GET', 'POST'])
@is_logged_in
def editFacility(facilityPropertyNumber):
    # create cursor
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * from facility where facilityPropertyNumber = %s", [facilityPropertyNumber])

    facility = cur.fetchone()

    form = AddFacilityForm()
    # populate fields
    form.facilityPropertyNumber.data = facility['facilityPropertyNumber']
    form.facilityName.data = facility['facilityName']
    form.availability.data = facility['availability']

    if request.method == 'POST' and form.validate():
        title = request.form['facilityName']
        body = request.form['availability']
        # create cursor
        cur = mysql.connection.cursor()
        # execute
        cur.execute("UPDATE facility SET facilityName=%s, availability=%s WHERE facilityPropertyNumber = %s", (title,body,facilityPropertyNumber))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()

        flash("Facility Updated.","success")

        return redirect(url_for('FacilityDashboard'))

    return render_template('editFacility.html', form=form)


@app.route('/editEquipment/<string:equipmentPropertyNumber>', methods=['GET','POST'])
@is_logged_in
def editEquipment(equipmentPropertyNumber):

    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM equipment WHERE equipmentPropertyNumber = %s', [equipmentPropertyNumber])
    equipment = cur.fetchone()
    form = AddEquipmentForm()
    form.equipmentPropertyNumber.data = equipment['equipmentPropertyNumber']
    form.equipmentName.data = equipment['equipmentName']
    form.quantity.data = equipment['quantity']
    if request.method == 'POST' and form.validate():
        equipName = request.form['equipmentName']
        quan = request.form['quantity']

        cur = mysql.connection.cursor()
        cur.execute('UPDATE equipment SET equipmentName=%s,quantity=%s WHERE equipmentPropertyNumber=%s', (equipName,quan,equipmentPropertyNumber))
        mysql.connection.commit()
        cur.close()

        flash('Equipment Updated','success')
        return redirect(url_for('EquipmentDashboard'))
    return render_template('editEquipment.html', form=form)

@app.route('/add-equipment', methods=['POST','GET'])
@is_logged_in
def addEquipment():
    form = AddEquipmentForm()
    if form.validate_on_submit():
        equipmentPropertyNumber = form.equipmentPropertyNumber.data
        equipmentName = form.equipmentName.data
        quantity = form.quantity.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO equipment(equipmentPropertyNumber,equipmentName,quantity) VALUES (%s,%s,%s)",
        (equipmentPropertyNumber,equipmentName,quantity))
        mysql.connection.commit()
        cur.close()

        flash("Equipment Added!","success")

        return redirect(url_for('index'))
    return render_template('add_equipment.html', form=form)

@app.route('/newres', methods=['POST','GET'])
@is_logged_in
def addReservation():
    form = ReservationForm()
    equip = {}
    fac = {}
    cur = mysql.connection.cursor()
    # GET DATA FROM DATABASE FOR EQUIPMENTS
    cur.execute("SELECT * FROM equipment")
    result = cur.fetchall()
    for res in result:
        equip[res["equipmentName"]] = res["equipmentPropertyNumber"]
    # GET DATA FROM DATABASE FOR FACILITIES
    cur.execute("SELECT * FROM facility")
    re = cur.fetchall()
    for r in re:
        fac[r["facilityName"]] = r["facilityPropertyNumber"]

    now = datetime.datetime.now()
    today = now.strftime("%d %B %Y")
    print(today)

    if form.validate_on_submit():
        # resFrom = form.resFrom.data
        # reseFrom = form.reseFrom.data
        # resTo = form.resTo.data
        # i = {}
        # x = ''.join(i)
        #
        # for r in equip:
        #     r = request.form.get(r)
        #     i.append(r)
        #
        #     # r = request.form[r]
        #     # i.append(r)
        #
        #
        # j = request.form['fac']
        # cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO reservation(equipment_id,facility_id,studentNumber,lastname,firstname) VALUES (%s,%s,%s,%s,%s)",(x,j,session.get("studentNumber"),session.get("lastName"),session.get("firstName")))
        # mysql.connection.commit()
        # cur.close()


        flash("Reservation Added", "Success")

        return redirect(url_for('index'))
    return render_template('createReservation.html',
        form=form,equip=equip,fac=fac)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET','POST'])
def register():
    form = StudentRegisterForm()
    if request.method == 'POST' and form.validate():
        studentNumber = form.studentNumber.data
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student(studentNumber,firstName,lastName,email,password)VALUES (%s,%s,%s,%s,%s)",
            (studentNumber,firstName,lastName,email,password))
        mysql.connection.commit()
        cur.close()

        flash("You are now registered, please login","success")

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        studentNumber = request.form['studentNumber']
        password_test = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM student WHERE studentNumber = %s',
            [studentNumber])
        if result > 0:
            # GET USER
            data = cur.fetchone()
            password = data['password']
            firstName = data['firstName']
            lastName = data['lastName']
            studentNumber = data['studentNumber']

            # COMPARE PASSWORDS
            if sha256_crypt.verify(password_test, password):
                # IF PASSED
                session['logged_in'] = True
                session['firstName'] = firstName
                session['lastName'] = lastName
                session['studentNumber'] = studentNumber

                flash("You are now Logged in","success")
                ## Might Change the directory for the return statement below
                return redirect(url_for('index'))
            else:
                error = 'Invalid Student Number/Password.'
                return render_template('login.html',error=error)
            cur.close()
        else:
            error = 'Invalid Student Number/Password.'
            return render_template('login.html',error=error)

    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin_layout.html')

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/logoutadmin')
@is_logged_in
def logoutAdmin():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

# Delete
@app.route('/delete_equipment/<string:equipmentPropertyNumber>', methods=['POST'])
@is_logged_in
def delete_equipment(equipmentPropertyNumber):
    # create cursor
    cur = mysql.connection.cursor()
    # delete
    cur.execute("DELETE FROM equipment WHERE equipmentPropertyNumber = %s", [equipmentPropertyNumber])
    # commit to database
    mysql.connection.commit()
    # close connection
    cur.close()

    flash("Equipment Deleted",'success')

    return redirect(url_for('EquipmentDashboard'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
