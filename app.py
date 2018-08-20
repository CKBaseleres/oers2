import os, sys,json
from flask import Flask, render_template, flash, redirect, jsonify, url_for, session, logging, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, TextAreaField, PasswordField, validators,BooleanField, IntegerField, widgets, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField, TimeRange
import datetime, pdfkit
from dateutil.parser import parse
import pandas as pd
from datetime import time, date, timedelta
from passlib.hash import sha256_crypt
from flask_paginate import Pagination, get_page_parameter
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from functools import wraps

from flask_migrate import Migrate

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/ors'

# MySql Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ors'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# app.config['SECRET_KEY'] = os.urandom(32)
app.config['SECRET_KEY'] = 'sercret123'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pupsj.ors@gmail.com'
app.config['MAIL_PASSWORD'] = 'pupadmin'


# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

# Initialize MySql
mysql = MySQL(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# manager = Manager(app)
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

def a_is_logged_in(a):
    @wraps(a)
    def wrap(*args, **kwargs):
        if 'a_logged_in' in session:
            return a(*args, **kwargs)
        else:
            flash('You are unauthorized for that page.','danger')
            return redirect(url_for('UserDashboard'))
    return wrap



######################## MODELS ############################
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentNumber = db.Column(db.String(15), unique=True, nullable=False)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    register_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    courseAndSec = db.Column(db.String(10), nullable=False) 
    contactNumber = db.Column(db.String(11), nullable=False)
    

    def reset(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'student_id':self.id}).decode('utf-8')

    @staticmethod
    def verify(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            student_id = s.loads(token)['student_id']
        except:
            return None
        return Student.query.get(student_id)

    def __repr__(self):
        return f"'{self.firstName}','{self.lastName}','{self.studentNumber}','{self.email}','{self.courseAndSec}'"

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    equipmentPropertyNumber = db.Column(db.String(50), unique=True, nullable=False)
    equipmentName = db.Column(db.String(50), nullable=False)
    categoryId = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.equipmentName}','{self.equipmentPropertyNumber}','{self.categoryId}'"

class Equipment_Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    categoryName = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.categoryName}'"

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilityPropertyNumber = db.Column(db.String(50), unique=True, nullable=False)
    facilityName = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"'{self.facilityName}','{self.availability}','{self.facilityPropertyNumber}'"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(50), nullable=True)
    facility_name = db.Column(db.String(50), nullable=True)
    studentNumber = db.Column(db.String(15), nullable=True)
    purpose = db.Column(db.String(100), nullable=False)
    dateFrom = db.Column(db.Date, nullable=False)
    timeFrom = db.Column(db.Time, nullable=False)
    timeTo = db.Column(db.Time, nullable=False)
    res_status = db.Column(db.String(15), nullable=False, default="Active")
    reservation_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    claimed_at = db.Column(db.String(50), nullable=True, default=" ")
    returned_at = db.Column(db.String(50), nullable=True, default=" ")
    description = db.Column(db.String(300), nullable= False)
    profOrOrg = db.Column(db.String(50),nullable = False)

    def __repr__(self):
        return f"'{self.equipment_name}','{self.facility_name}','{self.studentNumber}','{self.purpose}'\
        , '{self.dateFrom}','{self.timeFrom}','{self.timeTo}'"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.username}','{self.password}'"



######################## FORMS ############################
# Student Registration Form
class StudentRegisterForm(FlaskForm):
    def validate_studentNumber(form,field):
        student = Student.query.filter_by(studentNumber=field.data).first()
        if len(field.data) > 15 or len(field.data) < 15:
            raise ValueError('Student Number must be 15 characters long.')
        elif student:
            raise ValueError('That Student Number has already signed up.')

    def validate_email(form,field):
        student = Student.query.filter_by(email=field.data).first()
        if student:
            raise ValueError('That email is taken.')
    def validate_firstName(form,field):
        if field.data.isdigit():
            raise ValueError("Please input characters.")
    def validate_lastName(form,field):
        if field.data.isdigit():
            raise ValueError("Please input characters.")
    studentNumber = StringField('Student Number',
                                validators=[DataRequired()])
    firstName = StringField('First Name',
                            validators=[DataRequired(), Length(min=1, max=50)])
    lastName = StringField('Last Name',
                            validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('E-mail',
                        validators=[DataRequired(),Email(message='Invalid e-mail')])
    password = PasswordField('Password',
                            validators=[DataRequired(),Length(min=8), EqualTo('confirm', message='Passwords do not match.')])
    contactNumber = StringField('Contact Number',
                                validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                            EqualTo('password', message="Passwords do not match.")])
    crseSec = StringField('Course and Section',
                            validators=[Length(min=3, max=10)])
    submit = SubmitField('Sign Up')

class StudentUpdateForm(FlaskForm):
    studentNumber = StringField('Student Number',
                                validators=[DataRequired()])
    firstName = StringField('First Name',
                            validators=[DataRequired(), Length(min=1, max=50)])
    lastName = StringField('Last Name',
                            validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('E-mail',
                        validators=[DataRequired(),Email(message='Invalid e-mail')])
    crseSec = StringField('Course and Section',
                            validators=[Length(min=3, max=10)])
    submit = SubmitField('Update')

    def validate_studentNumber(form,field):
        if studentNumber.data != session.get['studentNumber']:
            student = Student.query.filter_by(studentNumber=field.data).first()
            if len(field.data) > 15 or len(field.data) < 15:
                raise ValueError('Student Number must be 15 characters long.')
            elif student:
                raise ValueError('That Student Number has already signed up.')

    def validate_email(form,field):
        if email.data != session.email:
            student = Student.query.filter_by(email=field.data).first()
            if student:
                raise ValueError('That email is taken.')

    def validate_firstName(form,field):
        if field.data.isdigit():
            raise ValueError("Please input characters.")
    def validate_lastName(form,field):
        if field.data.isdigit():
            raise ValueError("Please input characters.")



class AddEquipmentForm(FlaskForm):
    def validate_email(form,field):
        equip = Equipment.query.filter_by(equipmentPropertyNumber=field.data).first()
        if equip:
            raise ValueError('That Property number is already used.')
    equipmentPropertyNumber = StringField('Property Number',
                                        validators=[DataRequired(),Length(min=5, max=50)])
    equipmentName = StringField('Equipment Name',
                                validators=[DataRequired(),Length(min=1, max=50)])
    quantity = IntegerField('Quantity',
                            validators=[DataRequired(), NumberRange(message='Not a number value.')])

class AddFacilityForm(FlaskForm):
    def validate_email(form,field):
        fac = Facility.query.filter_by(facilityPropertyNumber=field.data).first()
        if fac:
            raise ValueError('That Property number is already used.')

    facilityPropertyNumber = StringField('Property Number',
                                        validators=[DataRequired(), Length(min=5, max=50)])
    facilityName = StringField('Facility Name',
                                validators=[DataRequired(), Length(min=3, max=50)])
    availability = SelectField('Availability',validators=[DataRequired()],
                                choices = [('Yes','Yes'),('No','No')])
    submit = SubmitField('Sign Up')


class ReservationForm(FlaskForm):
    checkbox = BooleanField('Agree?',)
    resFrom = DateField('Date', validators=[DataRequired()], format= "%Y-%m-%d")
    reseFrom = TimeField('From', format= "%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(17,00)
        ), DataRequired()])
    # reseFrom = StringField('Time')
    resTo = TimeField('To', format="%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(19,00)
        ), DataRequired()])
    purpose = SelectField('Purpose',validators=[DataRequired()],
        choices = [('Academic','Academic'),('Organizational Event','Organizational Event')])

class RequestResetForm(FlaskForm):
    email = StringField('E-mail',
                    validators=[DataRequired(),Email(message='Invalid e-mail')])
    submit = SubmitField('Request Password Reset')

    def validate_studentNumber(form,field):
        student = Student.query.filter_by(email=field.data).first()
        if student is None:
            raise ValueError('There is no account with that email. Please register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                        validators=[DataRequired(),Length(min=8), EqualTo('confirm', message='Password do not match.')])
    confirm = PasswordField('Confirm Password',
                        validators=[DataRequired()])
    submit = SubmitField('Reset Password')



# @app.route('/equipment/dashboard', methods=['GET'])
# @a_is_logged_in
# def EquipmentDashboard(equip_id):
#     equipment = Equipment.query.get_or_404(equip_id)
#     form = AddEquipmentForm()
#     if request.form == 'GET':
#         form.equipmentName.data = equipment.equipmentName
#         form.quantity.data = equipment.quantity
#         form.equipmentPropertyNumber.data = equipment.equipmentPropertyNumber
#     page = request.args.get('page',1,type=int)
#     equipments = Equipment.query.paginate(page=page,per_page=5)
#     if equipments is None:
#         msg = "No Equipments Found."
#         return render_template('equipmentDashboard.html', msg=msg)
#     else:
#         return render_template('equipmentDashboard.html', equipments=equipments,form=form,equip_id=equipment.id)

@app.route('/equipment/dashboard', methods=['GET'])
@a_is_logged_in
def EquipmentDashboard():
    page = request.args.get('page',1,type=int)
    equipments = Equipment.query.paginate(page=page,per_page=5)
    if equipments is None:
        msg = "No Equipments Found."
        return render_template('equipmentDashboard.html', msg=msg)
    else:
        return render_template('equipmentDashboard.html', equipments=equipments)


@app.route('/facility/dashboard')
@a_is_logged_in
def FacilityDashboard():
    page = request.args.get('page',1,type=int)
    facilities = Facility.query.paginate(page=page,per_page=5)
    if facilities is None:
        msg = "No Facilities Found."
        return render_template('facilityDashboard.html', msg=msg)
    else:
        return render_template('facilityDashboard.html', facilities=facilities)
    return render_template('facilityDashboard.html')

@app.route('/account',methods=['GET','POST'])
def editAccount():
    sn = str(session.get('studentNumber'))
    fn = str(session.get("firstName"))
    ln = str(session.get("lastName"))
    studentNumber = sn
    student = Student.query.filter(studentNumber==sn).first()
    form = StudentUpdateForm()
    if form.validate_on_submit():
        student.firstName = form.firstName.data
        student.lastName = form.lastName.data
        student.email = form.email.data
        # student.password = sha256_crypt.encrypt(str(form.password.data))
        student.courseAndSec = form.crseSec.data
        # student.studentNumber = sn
        db.session.commit()
        flash("Account updated.","success")
        return redirect(url_for('userDashboard'))
    elif request.method == 'GET':
        # Populate Fields
        form.studentNumber.data = sn
        form.firstName.data = fn
        form.lastName.data = ln
        # form.availability.data = facility.availability
        # form.facilityPropertyNumber.data = facility.facilityPropertyNumber
    return render_template('Uregister.html', form=form)

@app.route('/facility/<int:fac_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editFacility(fac_id):
    facility = Facility.query.get_or_404(fac_id)
    form = AddFacilityForm()
    if form.validate_on_submit():
        facility.facilityPropertyNumber = form.facilityPropertyNumber.data
        facility.facilityName = form.facilityName.data
        facility.availability = form.availability.data
        db.session.commit()
        flash("Facility Updated.","success")
        return redirect(url_for('FacilityDashboard', fac_id=facility.id))
    elif request.method == 'GET':
        # Populate Fields
        form.facilityName.data = facility.facilityName
        form.availability.data = facility.availability
        form.facilityPropertyNumber.data = facility.facilityPropertyNumber
    return render_template('editFacility.html', form=form)


@app.route('/equipment/<int:equip_id>/edit', methods=['GET','POST'])
@a_is_logged_in
def editEquipment(equip_id):
    equipment = Equipment.query.get_or_404(equip_id)
    form = AddEquipmentForm()
    if form.validate_on_submit():
        equipment.equipmentPropertyNumber = form.equipmentPropertyNumber.data
        equipment.equipmentName = form.equipmentName.data
        equipment.quantity = form.quantity.data
        db.session.commit()
        flash('Equipment Updated','success')
        return redirect(url_for('EquipmentDashboard', equip_id=equipment.id))
    elif request.method == 'GET':
        form.equipmentName.data = equipment.equipmentName
        form.quantity.data = equipment.quantity
        form.equipmentPropertyNumber.data = equipment.equipmentPropertyNumber
    return render_template('editEquipment.html', form=form)

@app.route('/reservation/<int:res_id>/edit', methods=['GET','POST'])
@is_logged_in
def editRes(res_id):
    res = Reservation.query.get_or_404(res_id)
    form = ReservationForm()

    equip = {}
    fac = {}
    # GET DATA FROM DATABASE FOR EQUIPMENTS
    equipments = Equipment.query.all()
    for resu in equipments:
        equip[resu.categoryId] = resu.equipmentPropertyNumber
    # GET DATA FROM DATABASE FOR FACILITIES
    facilities = Facility.query.filter(Facility.availability == 'Yes')
    for r in facilities:
        fac[r.facilityName] = r.facilityPropertyNumber
    
    print(res.dateFrom)
    print(res.purpose)
    print(res.description)

    if form.validate_on_submit():
        datee = form.resFrom.data
        ftime = form.reseFrom.data
        timeto = form.resTo.data
        purpose = form.purpose.data
        selectEquip= request.form['equips']
        selectFac = request.form['facs']
        orgOrProf = request.form['test']
        desc = request.form['desc']
        db.session.commit()
        flash('Reservation Updated','success')
        return redirect(url_for('UserDashboard', res_id=res.id))
    elif request.method == 'GET':
        form.resFrom.data = res.dateFrom
        form.reseFrom.data = res.timeFrom
        form.resTo.data = res.timeTo
        form.purpose.data = res.purpose
        # request.form['test'] = res.profOrOrg
        # request.args.get('test',' ') = res.profOrOrg
        # request.args.get('desc','') = res.description
        # request.args.get('equips','') = res.equipment_name
        # request.args.get('facs',' ') = res.facility_name
        
    return render_template('createReservation.html', form=form, equip=equip,fac=fac)

@app.route('/equipment/add', methods=['POST','GET'])
@a_is_logged_in
def addEquipment():
    form = AddEquipmentForm()
    if form.validate_on_submit():
        epn = form.equipmentPropertyNumber.data
        en = form.equipmentName.data
        quantity = form.quantity.data
        equipment = Equipment(equipmentPropertyNumber=epn,equipmentName=en,quantity=quantity)
        db.session.add(equipment)
        db.session.commit()

        flash("Equipment Added!","success")

        return redirect(url_for('UserDashboard'))
    return render_template('add_equipment.html', form=form)

@app.route('/facility/add', methods=['POST','GET'])
@a_is_logged_in
def addfacility():
    form = AddFacilityForm()
    if form.validate_on_submit():
        fpn = form.facilityPropertyNumber.data
        fn = form.facilityName.data
        availability = form.availability.data
        facility = Facility(facilityName=fn,availability=availability, facilityPropertyNumber=fpn)
        db.session.add(facility)
        db.session.commit()
        flash("Facility Added!","success")

        return redirect(url_for('FacilityDashboard'))
    return render_template('add_facility.html', form=form)

def send_letter(resFrom,resTime,resTo,today,equip,facility,purpose):
    # FOR PDF CREATION
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    rendered = render_template('pdf_template.html',
        resFrom=resFrom,
        reseFrom=resTime,
        today=today,
        purpose=purpose,
        equipment=equip,
        facility=facility,
        resTo=resTo
        )
    pdf = pdfkit.from_string(rendered, False ,configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=letter.pdf'
    return response

# Admin Reservation
@app.route('/adminReservation', methods=['POST', 'GET'])
@a_is_logged_in
def adminReservation():
    form = ReservationForm()
    equip = {}
    fac = {}

    equipments = Equipment.query.all()
    for res in equipments:
        equip[res.equipmentName] = res.equipmentPropertyNumber
    facilities = Facility.query.filter(Facility.availability == 'Yes')
    for r in facilities:
        fac[r.facilityName] = r.facilityPropertyNumber
    now = datetime.datetime.now()
    # datetoday = datetime.date.now()
    today = now.strftime("%d %B %Y")
    # print(today)
    if form.validate_on_submit():
        datee = form.resFrom.data
        ftime = form.reseFrom.data
        timeto = form.resTo.data
        purpose = form.purpose.data
        selectEquip= request.form['equips']
        selectFac = request.form['facs']
        orgOrProf = request.form['test']
        desc = request.form['desc']
        
        
        if(selectEquip == '--' and selectFac == '--'):
            flash("No equipment or facility has been selected.","danger")
        elif(orgOrProf == '--' or orgOrProf == ''):
            if(purpose == 'Academic'):
                flash("Please enter the name of your Professor.","danger")
            else:
                flash("Please select an organization.","danger")
        elif(desc == ''):
            flash("Please enter a description.","danger")
        # elif selectEquip != '--':
        #     countReservation = Reservation.query.filter(Reservation.equip == selectEquip).filter(Reservation.dateFrom == datee).count()
        #     # countEquip = Equipment.query.
        #     if countReservation >= countReservation:
        #         flash("Sorry no more aailable slots for that day.","danger")

        elif(datee < datetime.date.today()):
            flash("Invalid Date.",'danger')
        elif datee < (datetime.date.today() + timedelta(days=3)):
            flash("Reservations must be made for atleast 3 days before using",'danger')
        else:
            reservation = Reservation(equipment_name=selectEquip,facility_name=selectFac,purpose=purpose,dateFrom=datee,timeFrom=ftime,timeTo=timeto,studentNumber=session.get('username'),profOrOrg=orgOrProf,description=desc)
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation Added.", "success")

            return (redirect(url_for('UserDashboard')))

    return render_template('adminReservation.html',
        form=form,equip=equip,fac=fac)

    

@app.route('/newres', methods=['POST','GET'])
@is_logged_in
def addReservation():
    form = ReservationForm()
    equip = {}
    fac = {}
    # GET DATA FROM DATABASE FOR EQUIPMENTS
    equipments = Equipment.query.all()
    for res in equipments:
        equip[res.categoryId] = res.equipmentPropertyNumber
    # GET DATA FROM DATABASE FOR FACILITIES
    facilities = Facility.query.filter(Facility.availability == 'Yes')
    for r in facilities:
        fac[r.facilityName] = r.facilityPropertyNumber

    now = datetime.datetime.now()
    today = now.strftime("%d %B %Y")
    # print(today)
    if form.validate_on_submit():
        datee = form.resFrom.data
        ftime = form.reseFrom.data
        timeto = form.resTo.data
        purpose = form.purpose.data
        selectEquip= request.form['equips']
        selectFac = request.form['facs']
        orgOrProf = request.form['test']
        desc = request.form['desc']

        countReservationEquip = Reservation.query.filter(Reservation.equipment_name == selectEquip).filter(Reservation.dateFrom == datee).count()
        countEquip = Equipment.query.filter(Equipment.categoryId == selectEquip).count()
        countReservationFac = Reservation.query.filter(Reservation.facility_name == selectFac).filter(Reservation.dateFrom == datee).count()
        countFac = Facility.query.filter(Facility.facilityName == selectFac).count()
       

        if(selectEquip == '--' and selectFac == '--'):
            flash("No equipment or facility has been selected.","danger")
        elif(orgOrProf == '--' or orgOrProf == ''):
            if(purpose == 'Academic'):
                flash("Please enter the name of your Professor.","danger")
            else:
                flash("Please select an organization.","danger")
        elif(desc == ''):
            flash("Please enter a description.","danger")
        elif(selectFac == '--' and countReservationEquip == countEquip):
            flash("Sorry, no more available slots for "+ selectEquip+" on that day.","danger")
        elif(selectEquip == '--' and countReservationFac == countFac):
            flash("Sorry, no more avalable slots for "+selectFac+" on that day.","danger")
            print(countReservationFac)
            print(countFac)
        elif(selectEquip != '--' and selectFac != '--'):
            if(countReservationEquip == countEquip):
                flash("Sorry, no more available slots for "+ selectEquip+" on that day.","danger")
            elif(countReservationFac == countFac):
                flash("Sorry, no more available slots for "+selectFac+" on that day.","danger")
        elif(datee < datetime.date.today()):
            flash("Invalid Date.",'danger')
        elif datee < (datetime.date.today() + timedelta(days=3)):
            flash("Reservations must be made for atleast 3 days before using",'danger')
        elif timeto < ftime:
            flash("Incorrect time. Please check your time.", "dange")
        else:
            reservation = Reservation(equipment_name=selectEquip,facility_name=selectFac,purpose=purpose,dateFrom=datee,timeFrom=ftime,timeTo=timeto,studentNumber=session.get('studentNumber'),profOrOrg=orgOrProf,description=desc)
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation Added.", "success")

            return (redirect(url_for('UserDashboard')))

            # send_letter(date,ftime,timeto,today,selectEquip,selectFac,purpose)
            # FOR PDF CREATION
            # path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            # config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            # rendered = render_template('pdf_template.html',
            #     resFrom=date,
            #     reseFrom=ftime,
            #     today=today,
            #     purpose=purpose,
            #     equipment=selectEquip,
            #     facility=selectFac,
            #     timeTo=timeto
            #     )
            # pdf = pdfkit.from_string(rendered, False ,configuration=config)
            # response = make_response(pdf)
            # response.headers['Content-Type'] = 'application/pdf'
            # response.headers['Content-Disposition'] = 'attachment; filename=letter.pdf'
            # return response

        


    return render_template('createReservation.html',
        form=form,equip=equip,fac=fac)



@app.route('/register', methods=['GET','POST'])
def register():
    form = StudentRegisterForm()
    if request.method == 'POST' and form.validate():
        studentNumber = form.studentNumber.data
        firstName = form.firstName.data
        lastName = form.lastName.data
        contactNum = form.contactNumber.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        crseSec = form.crseSec.data
        student = Student(studentNumber=studentNumber,firstName=firstName,lastName=lastName,
        email=email,password=password,courseAndSec=crseSec,contactNumber=contactNum)
        db.session.add(student)
        db.session.commit()
        flash("You are now registered, please login","success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        studentNumber = request.form['studentNumber']
        password_test = request.form['password']
        student = Student.query.filter_by(studentNumber=studentNumber).first()
            # COMPARE PASSWORDS
        if student and sha256_crypt.verify(password_test, student.password ):
                # IF PASSED
            session['logged_in'] = True
            session['firstName'] = student.firstName
            session['lastName'] = student.lastName
            session['studentNumber'] = student.studentNumber
            # session['courseSection'] = student.cs

            flash("You are now Logged in","success")
                ## Might Change the directory for the return statement below
            return redirect(url_for('UserDashboard'))
        else:
            error = 'Invalid Student Number/Password.'
            return render_template('login.html',error=error)

    return render_template('login.html')


@app.route('/admin/login',methods=['GET','POST'])
def loginad():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:
                # IF PASSED
            session['a_logged_in'] = True
            session['username'] = username

            flash("You are now Logged in", "success")
            ## Might Change the directory for the return statement below
            return redirect(url_for('admin'))
        else:
            error = 'Invalid Username/Password.'
            # return redirect(url_for('index'))
            return render_template('adminsingin.html', error=error)
    return render_template('adminsingin.html')

def updateReservationStatus():
    reservations = Reservation.query.all()
    for reservation in reservations:
        if(reservation.res_status == 'Active'):
            if(reservation.dateFrom < datetime.date.today()):
                reservation.res_status = 'Done'
                db.session.commit()

updateReservationStatus()

@app.route('/admin/home')
@a_is_logged_in
def admin():
    page = request.args.get('page',1,type=int)
    reservations = Reservation.query.order_by(Reservation.dateFrom.asc()).filter(Reservation.res_status == 'Active').paginate(page=page,per_page=7)
    reservationss = Reservation.query.all()
    equipments = Equipment.query.all()
    facilities = Facility.query.all()
    return render_template('adminindex.html',equip=equipments,fac=facilities, reservations=reservations, reservationss=reservationss)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/logout')
@a_is_logged_in
def logoutAdmin():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservations')
def calendar():
    reservations = Reservation.query.all()
    return render_template('calendar.html', reservations=reservations)

@app.route('/data')
def return_data():
    reservation = []
    reservations = Reservation.query.filter(Reservation.res_status != 'Canceled')

    print(reservations)
    for res in reservations:
        if res.equipment_name == '--':
            item = res.facility_name
        else:
            item = res.equipment_name
        start = str(res.dateFrom)+"T"+str(res.timeFrom)
        end = str(res.dateFrom)+"T"+str(res.timeTo)
        reservatio = {
            "start" : start,
            "end" : end,
            "title" : item,
            "data" : {
                "timefrom" : str(res.timeFrom.strftime('%I:%M%p')),
                "timeto" : str(res.timeTo.strftime('%I:%M%p'))
            }
        }
        reservation.append(reservatio)
    return jsonify(reservation)

@app.route('/dashboard')
@is_logged_in
def UserDashboard():
    form = ReservationForm()
    equip = {}
    fac = {}
    # GET DATA FROM DATABASE FOR EQUIPMENTS
    equipments = Equipment.query.all()
    for res in equipments:
        equip[res.equipmentName] = res.equipmentPropertyNumber
    # GET DATA FROM DATABASE FOR FACILITIES
    facilities = Facility.query.filter(Facility.availability == 'Yes')
    for r in facilities:
        fac[r.facilityName] = r.facilityPropertyNumber

    sn = str(session.get("studentNumber"))
    page = request.args.get('page',1,type=int)
    reservations = Reservation.query.filter(Reservation.studentNumber == sn).order_by(Reservation.dateFrom.desc()).paginate(page=page,per_page=5)
    # cur = mysql.connection.cursor()
    if reservations is None:
        msg = "No Reservations Found."
        return render_template('userDashboard.html', msg=msg)
    else:
        return render_template('userDashboard.html', reservations=reservations, form=form, equip=equip, fac=fac)

@app.route('/reservations')
@is_logged_in
def allReservations():
    page = request.args.get('page',1,type=int)
    reservations = Reservation.query.filter(Reservation.res_status == 'Active').paginate(page=page,per_page=5)
    # reservations = Reservation.query.paginate(page=page,per_page=6)

    if reservations is None:
        msg = "No Equipments Found."
        return render_template('studReservationDashboard.html', msg=msg)
    else:
        return render_template('studReservationDashboard.html', reservations=reservations)

# Delete
@app.route('/dashboard/<int:res_id>/cancel',  methods=['POST'])
@is_logged_in
def cancelReservation(res_id):
    reservation = Reservation.query.filter_by(id = res_id).first()
    reservation.res_status = 'Canceled'
    db.session.commit()
    flash("Reservation Canceled!",'success')

    return redirect(url_for('UserDashboard'))

@app.route('/reservations/dashboard/<int:res_id>/cancel',  methods=['POST'])
@a_is_logged_in
def adminCancelReservation(res_id):
    reservation = Reservation.query.filter_by(id = res_id).first()
    reservation.res_status = 'Canceled'
    db.session.commit()
    flash("Reservation Canceled",'success')

    return redirect(url_for('resDashboard'))

# CLAIMING  
@app.route('/reservations/dashboard/<int:res_id>/claim',  methods=['POST'])
@a_is_logged_in
def addTime(res_id):
    reservation = Reservation.query.filter_by(id = res_id).first()
    today = datetime.datetime.now()
    if reservation.claimed_at == " ":
        reservation.claimed_at = today
    else:
        reservation.returned_at = today
    db.session.commit()

    return redirect(url_for('resDashboard'))

@app.route('/equipment/<int:equip_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_equipment(equip_id):
    equipments = Equipment.query.get_or_404(equip_id)
    db.session.delete(equipments)
    db.session.commit()
    flash("Equipment Deleted",'success')

    return redirect(url_for('EquipmentDashboard'))

def send_reset_email(student):
    token = student.reset()
    msg = Message('PUPSJ:OFERS Password Reset Request',
                    sender='pupsj.ors@gmail.com',
                    recipients=[student.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external = True)}

If this is not you. Just ignore this e-mail.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        send_reset_email(student)
        flash('An email has been sent to reset your password','success')
        return redirect(url_for('login'))
    return render_template('reset_request.html',form=form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    student = Student.verify(token)
    if student is None:
        flash('That is an invalid or expired token.','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = sha256_crypt.encrypt(form.password.data)
        student.password = password
        db.session.commit()
        flash("Your password has been updated","success")
        return redirect(url_for('login'))
    return render_template('reset_token.html',form=form)

@app.route("/reservations/dashboard", methods=['GET','POST'])
def resDashboard():
    page = request.args.get('page',1,type=int)
    # reservations = Reservation.query.join(Student, Student.studentNumber==Reservation.studentNumber).add_columns(Student.firstName, Student.lastName, Reservation.dateFrom, Reservation.timeFrom, Reservation.timeTo, Reservation.id, Reservation.equipment_name, Reservation.res_status, Reservation.facility_name, Reservation.purpose, Reservation.claimed_at, Reservation.returned_at).order_by(Reservation.dateFrom.desc()).paginate(page=page,per_page=6)
    # reservations = Reservation.query.paginate(page=page,per_page=6)

    reservations = Reservation.query.order_by(Reservation.dateFrom.desc()).paginate(page=page,per_page=6) 
    now = datetime.datetime.now()
    todayy = now.strftime("%Y-%m-%d")
    if reservations is None:
        msg = "No Equipments Found."
        return render_template('reservationDashboard.html', msg=msg)
    else:
        return render_template('reservationDashboard.html', reservations=reservations, todayy=todayy)

@app.route("/printReservation", methods=['GET'])
def printToday():
    today = datetime.date.today()
    reservations = Reservation.query.join(Student, Student.studentNumber==Reservation.studentNumber).add_columns(Student.firstName, Student.lastName, Reservation.dateFrom, Reservation.timeFrom, Reservation.timeTo, Reservation.id, Reservation.equipment_name, Reservation.facility_name, Reservation.purpose,Reservation.claimed_at, Reservation.returned_at).filter(Reservation.dateFrom==today).count()
    reservationss = Reservation.query.join(Student, Student.studentNumber==Reservation.studentNumber).add_columns(Student.firstName, Student.lastName, Reservation.dateFrom, Reservation.timeFrom, Reservation.timeTo, Reservation.id, Reservation.equipment_name, Reservation.facility_name, Reservation.purpose,Reservation.claimed_at, Reservation.returned_at).filter(Reservation.dateFrom==today)

    
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    rendered = render_template('reservationToday.html',reservations=reservations,reservationss=reservationss,today=today)
    pdf = pdfkit.from_string(rendered, False ,configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Reservations for '+str(today)+'.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()