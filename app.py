from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from flask_wtf import Form
from wtforms import StringField, TextAreaField, PasswordField, validators, BooleanField, DateTimeField, IntegerField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__, static_url_path="/static", static_folder="static")

# MySql Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'capstone'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySql
mysql = MySQL(app)

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
class StudentRegisterForm(Form):
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

class AddEquipmentForm(Form):
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

class AddFacilityForm(Form):
    facilityPropertyNumber = StringField('Property Number',
        [validators.length(min=5, max=50)],
        render_kw={
            "class": "form-control"
        })
    facilityName = StringField('Equipment Name',
        [validators.length(min=1, max=50)],
        render_kw={
            "class": "form-control"
        })
    availability = StringField('Availability',
        [validators.length(min=2, max=3)],
        render_kw={
            "class": "form-control"
        })

class ReservationForm(Form):
    checkbox = BooleanField('Agree?', [validators.DataRequired(), ])
    equip = ["equip1","equip2","equip3"]
    fac = ["fac1","fac2","fac3"]
    for i in equip:
        i = BooleanField('Equipments',  [validators.DataRequired()])
    for j in fac:
        j = BooleanField('Facilities', [validators.DataRequired()])
    res = DateTimeField('From',
        render_kw={"type": "datetime-local",
                    "id":"datetime"
                    })
    rese = DateTimeField('To',render_kw={"type": "time"})

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
    equip = ["equip1","equip2","equip3"]
    fac = ["fac1","fac2","fac3"]
    if form.validate_on_submit():
        for i in equip:
            return str(form.i.data)
        for j in fac:
            return str(form.j.data)
        res = form.res.data
        rese = form.rese.data
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
    form = StudentRegisterForm(request.form)
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

            # COMPARE PASSWORDS
            if sha256_crypt.verify(password_test, password):
                # IF PASSED
                session['logged_in'] = True
                session['firstName'] = firstName
                session['lastName'] = lastName

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
