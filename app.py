import os, sys,json,string, random, re
from flask import Flask, render_template, flash, redirect, jsonify, url_for, session, logging, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, TextAreaField, PasswordField, validators,BooleanField, IntegerField, widgets, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField, TimeRange, DateRange
import datetime, pdfkit
from dateutil.parser import parse
# import pandas as pd
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
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'pupsj.ors@gmail.com'
app.config['MAIL_PASSWORD'] = 'pupadmin'


# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

# Initialize MySql
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
    facilityName = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"'{self.facilityName}','{self.availability}'"

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
    reference = db.Column(db.String(13), nullable=False)
    description = db.Column(db.String(300), nullable= False)
    profOrOrg = db.Column(db.String(50),nullable = False)

    def __repr__(self):
        return f"'{self.equipment_name}','{self.facility_name}','{self.studentNumber}','{self.purpose}'\
        , '{self.dateFrom}','{self.timeFrom}','{self.timeTo}','{self.reference}'"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return f"'{self.username}','{self.password}'"

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50),nullable=False)
    fieldOfStudy = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}','{self.fieldOfStudy}'"

class FieldOfStudy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}'"

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}','{self.course}'"

class Purpose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}'"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}'"

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"'{self.name}'"


######################## FORMS ############################
# Student Registration Form
class StudentRegisterForm(FlaskForm):
    def validate_studentNumber(form,field):
        student = Student.query.filter_by(studentNumber=field.data).first()
        re1='((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'	# Year 1
        re2='(-)'	# Any Single Character 1
        re3='(\\d)'	# Any Single Digit 1
        re4='(\\d)'	# Any Single Digit 2
        re5='(\\d)'	# Any Single Digit 3
        re6='(\\d)'	# Any Single Digit 4
        re7='(\\d)'	# Any Single Digit 5
        re8='(-)'	# Any Single Character 2
        re9='((?:[a-z][a-z]+))'	# Word 1
        re10='(-)'	# Any Single Character 3
        re11='(\\d)'	# Any Single Digit 6

        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11,re.IGNORECASE|re.DOTALL)
        m = rg.search(field.data)
        if not m:
            raise ValueError('Invalid Student Number.')
        elif student:
            raise ValueError('That Student Number has already signed up.')
        elif len(field.data) > 15:
            raise ValueError('Invalid ')
    


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
    
    def validate_contactNumber(form,field):
        if field.data.isalpha():
            raise ValueError("Please input numbers.")
        elif len(field.data) > 11:
            raise ValueError("Invalid Number")
        
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
    course = SelectField('Course',
                            validators=[DataRequired()],
                            choices=[])
    section = SelectField('Section',
                            validators=[DataRequired()],
                            choices=[])
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
    categoryId = SelectField('Category',
                            validators=[DataRequired()],
                            choices=[])

class AddFacilityForm(FlaskForm):
    def validate_email(form,field):
        fac = Facility.query.filter_by(facilityName=field.data).first()
        if fac:
            raise ValueError('That Facility Name is already used.')

    facilityName = StringField('Facility Name',
                                validators=[DataRequired(), Length(min=3, max=50)])
    availability = SelectField('Accessible',validators=[DataRequired()],
                                choices = [('Yes','Yes'),('No','No')])
    submit = SubmitField('Sign Up')

class DateForm(FlaskForm):
    firstDate = StringField('From', validators=[DataRequired()])
    secondDate = StringField('To', validators=[DataRequired()])

class FieldOfStudyForm(FlaskForm):
    name = StringField('Field', validators=[DataRequired()])

class ReservationForm(FlaskForm):
    checkbox = BooleanField('Agree?',)
    equipment = SelectField('Equipment', choices=[])
    facility = SelectField('Facilities', choices=[])
    resFrom = StringField('Date', validators=[DataRequired()]) #%Y-%m-%d
    reseFrom = TimeField('From', format= "%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(17,00)
        ), DataRequired()])
    # reseFrom = StringField('Time')
    resTo = TimeField('To', format="%H:%M",validators=[TimeRange(
            min=time(7,30),
            max=time(21,00)
        ), DataRequired()])
    purpose = SelectField('Purpose',validators=[DataRequired()],
        choices = [])
    desc = TextAreaField('Description*')
    

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

class CourseForm(FlaskForm):
    name = StringField('Course',
                        validators=[DataRequired()])

class ProfessorForm(FlaskForm):
    firstName = StringField('First Name',
                        validators=[DataRequired()])
    lastName = StringField('Last Name',
                        validators=[DataRequired()])
    fieldOfStudy = SelectField('Field Of Study',
                                validators=[DataRequired()],
                                choices=[])

class OrganizationForm(FlaskForm):
    name = StringField('Organization Name',
                        validators=[DataRequired()])
    course = SelectField('Course Associated',
                        choices=[])

class PurposeForm(FlaskForm):
    name = StringField('Purpose',
                        validators=[DataRequired()])

class CategoryForm(FlaskForm):
    name = StringField('Category',
                        validators=[DataRequired()])
###################### EQUIP CATEGORY ####################
@app.route('/category', methods=['GET','POST'])
@a_is_logged_in
def AllCategory():
    page = request.args.get('page',1,type=int)
    categories = Equipment_Category.query.filter(Equipment_Category.categoryName != '--').paginate(page=page,per_page=5)
    if categories is None:
        msg = "No Categories Found."
        return render_template('dashboardCategory.html', msg=msg)
    else:
        return render_template('dashboardCategory.html', categories=categories)

@app.route('/category/new', methods=['GET','POST'])
@a_is_logged_in
def NewCategory():
    form = CategoryForm()
    title = "Add Category"
    if form.validate_on_submit():
        name = form.name.data
        field = Equipment_Category(name=name)
        db.session.add(field)
        db.session.commit()

        flash("Equipment Category Added!","success")

        return redirect(url_for('AllCategory'))
    return render_template('add_category.html', form=form, title=title)

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editCategory(category_id):
    field = Equipment_Category.query.get_or_404(category_id)
    title = "Edit Category"
    form = CategoryForm()
    if form.validate_on_submit():
        field.categoryName = form.name.data
        db.session.commit()
        flash("Category Updated.","success")
        return redirect(url_for('AllCategory', category_id=Equipment_Category.id))
    elif request.method == 'GET':
        # Populate Fields
        form.name.data = field.categoryName
    return render_template('add_category.html', form=form, title=title)
###################### FIELD OF STUDY ####################
@app.route('/fieldOfStudy', methods=['GET','POST'])
@a_is_logged_in
def AllFields():
    page = request.args.get('page',1,type=int)
    studies = FieldOfStudy.query.filter(FieldOfStudy.name != '--').paginate(page=page,per_page=5)
    if studies is None:
        msg = "No Fields Found."
        return render_template('dashboardFieldOfStudy.html', msg=msg)
    else:
        return render_template('dashboardFieldOfStudy.html', studies=studies)

@app.route('/fieldOfStudy/new', methods=['GET','POST'])
@a_is_logged_in
def NewField():
    form = FieldOfStudyForm()
    title = "Add Field Of Study"
    if form.validate_on_submit():
        name = form.name.data
        field = FieldOfStudy(name=name)
        db.session.add(field)
        db.session.commit()

        flash("Field of Study Added!","success")

        return redirect(url_for('AllFields'))
    return render_template('add_field.html', form=form, title=title)

@app.route('/fieldOfStudy/<int:field_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editField(field_id):
    field = FieldOfStudy.query.get_or_404(field_id)
    title = "Edit Field of Study"
    form = FieldOfStudyForm()
    if form.validate_on_submit():
        field.name = form.name.data
        db.session.commit()
        flash("Field of Study Updated.","success")
        return redirect(url_for('AllField', field_id=field.id))
    elif request.method == 'GET':
        # Populate Fields
        form.name.data = field.name
    return render_template('add_field.html', form=form, title=title)

@app.route('/fieldOfStudy/<int:field_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_field(field_id):
    field = FieldOfStudy.query.get_or_404(field_id)
    db.session.delete(field)
    db.session.commit()
    flash("Course Deleted",'success')

    return redirect(url_for('AllCourses'))


###################### COURSES ######################
@app.route('/courses', methods=['GET','POST'])
@a_is_logged_in
def AllCourses():
    page = request.args.get('page',1,type=int)
    courses = Course.query.paginate(page=page,per_page=5)
    if courses is None:
        msg = "No Courses Found."
        return render_template('coursesDashboard.html', msg=msg)
    else:
        return render_template('coursesDashboard.html', courses=courses)

@app.route('/courses/new', methods=['GET','POST'])
@a_is_logged_in
def NewCourse():
    form = CourseForm()
    title = "Add Course"
    if form.validate_on_submit():
        name = form.name.data
        course = Course(name=name)
        db.session.add(course)
        db.session.commit()

        flash("Course Added!","success")

        return redirect(url_for('AllCourses'))
    return render_template('add_course.html', form=form, title=title)

@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editCourse(course_id):
    course = Course.query.get_or_404(course_id)
    title = "Edit Course"
    form = CourseForm()
    if form.validate_on_submit():
        course.name = form.name.data
        db.session.commit()
        flash("Course Updated.","success")
        return redirect(url_for('AllCourses', course_id=course.id))
    elif request.method == 'GET':
        # Populate Fields
        form.name.data = course.name
    return render_template('add_course.html', form=form, title=title)

@app.route('/courses/<int:course_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course Deleted",'success')

    return redirect(url_for('AllCourses'))

# @app.route('/facility/<int:course_id>/edit', methods=['GET', 'POST'])
# @a_is_logged_in
# def editCourse(course_id):
#     course = Course.query.get_or_404(course_id)
#     form = CourseForm()
#     if form.validate_on_submit():
#         course.name = form.facilityPropertyNumber.data
#         db.session.commit()
#         flash("Course Updated.","success")
#         return redirect(url_for('FacilityDashboard', course_id=facility.id))
#     elif request.method == 'GET':
#         # Populate Fields
#         form.facilityName.data = facility.facilityName
#         form.availability.data = facility.availability
#         form.facilityPropertyNumber.data = facility.facilityPropertyNumber
#     return render_template('editFacility.html', form=form)

########################## PURPOSES #############################

@app.route('/purposes', methods=['GET','POST'])
@a_is_logged_in

def AllPurposes():
    page = request.args.get('page',1,type=int)
    purposes = Purpose.query.filter(Purpose.name != '--').paginate(page=page,per_page=5)
    if purposes is None:
        msg = "No Courses Found."
        return render_template('purposesDashboard.html', msg=msg)
    else:
        return render_template('purposesDashboard.html', purposes=purposes)

@app.route('/purposes/new', methods=['GET','POST'])
@a_is_logged_in
def NewPurpose():
    form = PurposeForm()
    title = 'Add Purpose'
    if form.validate_on_submit():
        name = form.name.data
        course = Purpose(name=name)
        db.session.add(course)
        db.session.commit()

        flash("Purpose Added!","success")

        return redirect(url_for('AllPurposes'))
    return render_template('add_purpose.html', form=form, title=title)

@app.route('/purposes/<int:purpose_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editPurpose(purpose_id):
    purpose = Purpose.query.get_or_404(purpose_id)
    title = "Edit Purpose"
    form = PurposeForm()
    if form.validate_on_submit():
        purpose.name = form.name.data
        db.session.commit()
        flash("Purpose Updated.","success")
        return redirect(url_for('AllPurposes', purpose_id=purpose.id))
    elif request.method == 'GET':
        # Populate Fields
        form.name.data = purpose.name
    return render_template('add_purpose.html', form=form, title=title)

@app.route('/purposes/<int:purpose_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_purpose(purpose_id):
    purpose = Purpose.query.get_or_404(purpose_id)
    db.session.delete(purpose)
    db.session.commit()
    flash("Purpose Deleted",'success')
    return redirect(url_for('AllPurposes'))



################################### ORGANIZATIONS ############################33

@app.route('/organizations', methods=['GET','POST'])
@a_is_logged_in
def AllOrgranizations():
    page = request.args.get('page',1,type=int)
    organizations = Organization.query.paginate(page=page,per_page=5)
    if organizations is None:
        msg = "No Organizations Found."
        return render_template('organizationsDashboard.html', msg=msg)
    else:
        return render_template('organizationsDashboard.html', organizations=organizations)

@app.route('/organizations/new', methods=['GET','POST'])
@a_is_logged_in
def NewOrganization():
    form = OrganizationForm()
    title = "Add Organization"
    form.course.choices = [(crse.name,crse.name) for crse in Course.query.order_by(Course.name.asc()).all()]
    if form.validate_on_submit():
        name = form.name.data
        crse = form.course.data
        organization = Organization(name=name,course=crse)
        db.session.add(organization)
        db.session.commit()

        flash("Organization Added!","success")

        return redirect(url_for('AllOrgranizations'))
    return render_template('add_organization.html', form=form, title=title)

@app.route('/organizations/<int:organization_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editOrganization(organization_id):
    org = Organization.query.get_or_404(organization_id)
    title = "Edit Organization"
    form = OrganizationForm()
    form.course.choices = [(crse.name,crse.name) for crse in Course.query.order_by(Course.name.asc()).all()]
    if form.validate_on_submit():
        org.name = form.name.data
        org.course = form.course.data
        db.session.commit()
        flash("Organization Updated.","success")
        return redirect(url_for('AllOrgranizations', organization_id=org.id))
    elif request.method == 'GET':
        form.name.data = org.name
        form.course.data = org.course
    return render_template('add_organization.html', form=form, title=title)

@app.route('/organizations/<int:org_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_org(org_id):
    org = Organization.query.get_or_404(org_id)
    db.session.delete(org)
    db.session.commit()
    flash("Organization Deleted",'success')

    return redirect(url_for('AllOrgranizations'))


################################## PROFESSORS #############################
@app.route('/professors', methods=['GET','POST'])
@a_is_logged_in
def AllProfessors():
    page = request.args.get('page',1,type=int)
    professors = Professor.query.order_by(Professor.id.desc()).paginate(page=page,per_page=5)
    if professors is None:
        msg = "No Professors Found."
        return render_template('professorsDashboard.html', msg=msg)
    else:
        return render_template('professorsDashboard.html', professors=professors)

@app.route('/professors/new', methods=['GET','POST'])
@a_is_logged_in
def NewProfessor():
    form = ProfessorForm()
    form.fieldOfStudy.choices = [(field.name,field.name) for field in FieldOfStudy.query.order_by(FieldOfStudy.name.asc()).all()]
    title = "Add Professor"
    if form.validate_on_submit():
        fname = form.firstName.data
        lname = form.lastName.data
        fieldOfStudy = form.fieldOfStudy.data
        professor = Professor(firstName=fname,lastName=lname,fieldOfStudy=fieldOfStudy)
        db.session.add(professor)
        db.session.commit()

        flash("Professor Added!","success")

        return redirect(url_for('AllProfessors'))
    return render_template('add_professor.html', form=form, title=title)

@app.route('/professors/<int:prof_id>/edit', methods=['GET', 'POST'])
@a_is_logged_in
def editProfessor(prof_id):
    prof = Professor.query.get_or_404(prof_id)
    title = "Edit Professor"
    form = ProfessorForm()
    if form.validate_on_submit():
        prof.name = form.name.data
        prof.fieldOfStudy = form.fieldOfStudy.data
        db.session.commit()
        flash("Professor Updated.","success")
        return redirect(url_for('AllProfessors', prof_id=prof.id))
    elif request.method == 'GET':
        form.name.data = prof.name
        form.fieldOfStudy.data = prof.fieldOfStudy
    return render_template('add_professor.html', form=form, title=title)

@app.route('/professors/<int:prof_id>/delete',  methods=['POST'])
@a_is_logged_in
def delete_professor(prof_id):
    prof = Professor.query.get_or_404(prof_id)
    db.session.delete(prof)
    db.session.commit()
    flash("Professor Deleted",'success')

    return redirect(url_for('AllProfessors'))





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
    form = AddEquipmentForm()
    page = request.args.get('page',1,type=int)
    equipments = Equipment.query.filter(Equipment.equipmentName != '--').paginate(page=page,per_page=5)
    if equipments is None:
        msg = "No Equipments Found."
        return render_template('equipmentDashboard.html', msg=msg)
    else:
        return render_template('equipmentDashboard.html', equipments=equipments, form=form)


@app.route('/facility/dashboard')
@a_is_logged_in
def FacilityDashboard():
    page = request.args.get('page',1,type=int)
    facilities = Facility.query.filter(Facility.facilityName != '--').paginate(page=page,per_page=5)
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
        # facility.facilityPropertyNumber = form.facilityPropertyNumber.data
        facility.facilityName = form.facilityName.data
        facility.availability = form.availability.data
        db.session.commit()
        flash("Facility Updated.","success")
        return redirect(url_for('FacilityDashboard', fac_id=facility.id))
    elif request.method == 'GET':
        # Populate Fields
        form.facilityName.data = facility.facilityName
        form.availability.data = facility.availability
        # form.facilityPropertyNumber.data = facility.facilityPropertyNumber
    return render_template('editFacility.html', form=form)


@app.route('/equipment/<int:equip_id>/edit', methods=['GET','POST'])
@a_is_logged_in
def editEquipment(equip_id):
    equipment = Equipment.query.get_or_404(equip_id)
    form = AddEquipmentForm()
    title = 'Edit Equipment'
    if form.validate_on_submit():
        equipment.equipmentPropertyNumber = form.equipmentPropertyNumber.data
        equipment.equipmentName = form.equipmentName.data
        equipment.categoryId = form.categoryId.data
        db.session.commit()
        flash('Equipment Updated','success')
        return redirect(url_for('EquipmentDashboard', equip_id=equipment.id))
    elif request.method == 'GET':
        form.equipmentName.data = equipment.equipmentName
        form.categoryId.data =  equipment.categoryId
        form.equipmentPropertyNumber.data = equipment.equipmentPropertyNumber
    return render_template('add_equipment.html', form=form, title=title)

# @app.route('/reservation/<int:res_id>/show' methods=['GET'])
# @is_logged_in
# def showReservation(res_id)
#     res = Reservation.query.get_or_404(res_id)
    
    

@app.route('/reservations/<int:res_id>/edit', methods=['GET','POST'])
@a_is_logged_in
def editRes(res_id):
    res = Reservation.query.get_or_404(res_id)
    form = ReservationForm()

    # equip = {}
    # fac = {}
    # # GET DATA FROM DATABASE FOR EQUIPMENTS
    # equipments = Equipment.query.all()
    # for resu in equipments:
    #     equip[resu.categoryId] = resu.equipmentPropertyNumber
    # # GET DATA FROM DATABASE FOR FACILITIES
    # facilities = Facility.query.filter(Facility.availability == 'Yes')
    # for r in facilities:
    #     fac[r.facilityName] = r.facilityPropertyNumber
    form.purpose.choices = [(purp.name,purp.name) for purp in Purpose.query.order_by(Purpose.name.asc()).all()]
    form.equipment.choices = [(equipment.categoryName,equipment.categoryName) for equipment in Equipment_Category.query.order_by(Equipment_Category.categoryName.asc()).all()]

    form.facility.choices = [(facility.facilityName, facility.facilityName) for facility in Facility.query.filter(Facility.availability == 'Yes')]

    if form.validate_on_submit():
        datee = datetime.datetime.strptime(form.resFrom.data, '%Y-%m-%d').date()
        ftime = form.reseFrom.data
        reference = id_generator()
        timeto = form.resTo.data
        purpose = form.purpose.data
        selectEquip= form.equipment.data
        selectFac = form.facility.data
        orgOrProf = request.form['test']
        desc = request.form['desc']
        db.session.commit()
        flash('Reservation Updated','success')
        return redirect(url_for('resDashboard', res_id=res.id))
    elif request.method == 'GET':
        form.resFrom.data = res.dateFrom
        form.reseFrom.data = res.timeFrom
        form.resTo.data = res.timeTo
        form.purpose.data = res.purpose
        form.equipment.data = res.equipment_name
        form.facility.data = res.facility_name
        # request.form['test'] = res.profOrOrg
        # request.args.get('test',' ') = res.profOrOrg
        # request.args.get('desc','') = res.description
        # request.args.get('equips','') = res.equipment_name
        # request.args.get('facs',' ') = res.facility_name
        
    return render_template('adminReservation.html', form=form)

@app.route('/equipment/add', methods=['POST','GET'])
@a_is_logged_in
def addEquipment():
    form = AddEquipmentForm()
    title = 'Add Equipment'
    form.categoryId.choices = [(equipment.categoryName,equipment.categoryName) for equipment in Equipment_Category.query.order_by(Equipment_Category.categoryName.asc()).all()]
    if form.validate_on_submit():
        epn = form.equipmentPropertyNumber.data
        en = form.equipmentName.data
        quantity = form.categoryId.data
        equipment = Equipment(equipmentPropertyNumber=epn,equipmentName=en,categoryId=quantity)
        db.session.add(equipment)
        db.session.commit()

        flash("Equipment Added!","success")

        return redirect(url_for('EquipmentDashboard'))
    return render_template('add_equipment.html', form=form, title=title)

@app.route('/facility/add', methods=['POST','GET'])
@a_is_logged_in
def addfacility():
    form = AddFacilityForm()
    if form.validate_on_submit():
        fn = form.facilityName.data.capitalize()
        availability = form.availability.data
        facility = Facility(facilityName=fn,availability=availability)
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

    def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    form.purpose.choices = [(purp.name,purp.name) for purp in Purpose.query.order_by(Purpose.name.asc()).all()]
    form.equipment.choices = [(equipment.categoryName,equipment.categoryName) for equipment in Equipment_Category.query.order_by(Equipment_Category.categoryName.asc()).all()]

    form.facility.choices = [(facility.facilityName, facility.facilityName) for facility in Facility.query.order_by(Facility.facilityName.asc()).filter(Facility.availability == 'Yes')]
    now = datetime.datetime.now()
    today = now.strftime("%d %B %Y")
    # print(today)
    if form.validate_on_submit():
        datee = form.resFrom.data
        ftime = form.reseFrom.data
        timeto = form.resTo.data
        purpose = form.purpose.data
        reference = id_generator()
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
            reservation = Reservation(equipment_name=selectEquip,facility_name=selectFac,purpose=purpose,dateFrom=datee,timeFrom=ftime,timeTo=timeto,studentNumber=session.get('username'),profOrOrg=orgOrProf,description=desc,reference=reference)
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation Added.", "success")

            return (redirect(url_for('UserDashboard')))

    return render_template('adminReservation.html',
        form=form)

def send_confirmation(student):
    msg = Message('PUPSJ:OFERS Confirmed Reservation',
                    sender='pupsj.ors@gmail.com',
                    recipients=[str(session.get('email'))])
    msg.body = f'''Thank you for using our Reservation System. Your reservation for {student} has been added. '''
    mail.send(msg)

@app.route('/newres', methods=['POST','GET'])
@is_logged_in
def addReservation():
    form = ReservationForm()
    # 12 digit generator
    def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    form.purpose.choices = [(purp.name,purp.name) for purp in Purpose.query.order_by(Purpose.name.asc()).all()]
    form.equipment.choices = [(equipment.categoryName,equipment.categoryName) for equipment in Equipment_Category.query.order_by(Equipment_Category.categoryName.asc()).all()]

    form.facility.choices = [(facility.facilityName, facility.facilityName) for facility in Facility.query.order_by(Facility.facilityName.asc()).filter(Facility.availability == 'Yes')]
    now = datetime.datetime.now()
    today = now.strftime("%d %B %Y")
    # print(today)
    if form.validate_on_submit():
        # datee = form.resFrom.data.datetime.datetime.strftime("%Y-%m-%d")
        datee = datetime.datetime.strptime(form.resFrom.data, '%Y-%m-%d').date()
        ftime = form.reseFrom.data
        reference = id_generator()
        timeto = form.resTo.data
        purpose = form.purpose.data
        selectEquip= form.equipment.data
        selectFac = form.facility.data
        orgOrProf = request.form['test']
        desc = request.form['desc']

        countReservationEquip = Reservation.query.filter(Reservation.equipment_name == selectEquip).filter(Reservation.dateFrom == datee).count()
        countEquip = Equipment.query.filter(Equipment.categoryId == selectEquip).count()
        countReservationFac = Reservation.query.filter(Reservation.facility_name == selectFac).filter(Reservation.dateFrom == datee).count()
        countFac = Facility.query.filter(Facility.facilityName == selectFac).count()
       

        if(selectEquip == '--' and selectFac == '--'):
            flash("No equipment or facility has been selected.","danger")
        elif(countReservationEquip == countEquip):
            flash("Sorry, no more available slots for "+ selectEquip+" on that day.","danger")
        elif(countReservationFac == countFac):
            print(countReservationFac)
            flash("Sorry, no more available slots for "+selectFac+" on that day.","danger")
        elif(selectFac == '--' and countReservationEquip == countEquip):
            flash("Sorry, no more available slots for "+ selectEquip+" on that day.","danger")
        elif(selectEquip == '--' and countReservationFac == countFac):
            flash("Sorry, no more avalable slots for "+selectFac+" on that day.","danger")
        elif(datee < datetime.date.today()):
            flash("Invalid Date.",'danger')
        elif datee < (datetime.date.today() + timedelta(days=3)):
            flash("Reservations must be made for atleast 3 days before using",'danger')
        elif timeto < ftime:
            flash("Incorrect time. Please check your time.", "dange")
        else:
            send_confirmation(datee)
            reservation = Reservation(equipment_name=selectEquip,facility_name=selectFac,purpose=purpose,dateFrom=datee,timeFrom=ftime,timeTo=timeto,studentNumber=session.get('studentNumber'),profOrOrg=orgOrProf,description=desc, reference=reference)
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
        form=form)

@app.route('/reservation/<int:res_id>/show', methods=['GET'])
@is_logged_in
def showReservation(res_id):
    form = ReservationForm()
    res = Reservation.query.get_or_404(res_id)
    equip = res.equipment_name
    fac = res.facility_name
    purpose = res.purpose
    dateFrom = res.dateFrom
    timeFrom = res.timeFrom
    timeTo = res.timeTo
    status = res.res_status
    resdate  = res.reservation_date
    ref = res.reference
    porg = res.profOrOrg
    claim = res.claimed_at
    returnn = res.returned_at

    return render_template('view_reservation.html', form=form,equip=equip, fac=fac,purpose=purpose,dateFrom=dateFrom,timeFrom=timeFrom,timeTo=timeTo,status=status,resdate=resdate, ref=ref,porg=porg,claim=claim,returnn=returnn)



@app.route('/register', methods=['GET','POST'])
def register():
    form = StudentRegisterForm()
    form.course.choices = [(crse.name,crse.name) for crse in Course.query.order_by(Course.name.asc()).all()]
    form.section.choices = [(sec.name,sec.name) for sec in Section.query.order_by(Section.name.asc()).all()]
    if request.method == 'POST' and form.validate():
        studentNumber = form.studentNumber.data
        firstName = form.firstName.data
        lastName = form.lastName.data
        contactNum = form.contactNumber.data
        course = form.course.data
        sec = form.section.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        crseSec = course+' '+sec
        student = Student(studentNumber=studentNumber,firstName=firstName,lastName=lastName,
        email=email,password=password,courseAndSec=crseSec,contactNumber=contactNum)
        db.session.add(student)
        db.session.commit()
        flash("You are now registered, please login","success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# @app.route('/login',methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         studentNumber = request.form['studentNumber']
#         password_test = request.form['password']
#         student = Student.query.filter_by(studentNumber=studentNumber).first()
#             # COMPARE PASSWORDS
#         if student and sha256_crypt.verify(password_test, student.password ):
#                 # IF PASSED
#             session['logged_in'] = True
#             session['firstName'] = student.firstName
#             session['lastName'] = student.lastName
#             session['studentNumber'] = student.studentNumber
#             # session['courseSection'] = student.cs

#             flash("You are now Logged in","success")
#                 ## Might Change the directory for the return statement below
#             return redirect(url_for('UserDashboard'))
#         else:
#             error = 'Invalid Student Number/Password.'
#             return render_template('login.html',error=error)

#     return render_template('login.html')


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
    reservations = Reservation.query.order_by(Reservation.dateFrom.asc()).filter(Reservation.res_status == 'Active').limit(9)
    reservationss = Reservation.query.all()
    equipments = Equipment.query.filter(Equipment.equipmentName != '--').all()
    facilities = Facility.query.filter(Facility.facilityName != '--').all()
    return render_template('adminindex.html',equip=equipments,fac=facilities, reservations=reservations, reservationss=reservationss)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin/logout')
@a_is_logged_in
def logoutAdmin():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/' ,methods=['GET','POST'])
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
            session['email'] = student.email
            # session['courseSection'] = student.cs

            flash("You are now Logged in","success")
                ## Might Change the directory for the return statement below
            return redirect(url_for('UserDashboard'))
        else:
            error = 'Invalid Student Number/Password.'
            return render_template('login.html',error=error)

    return render_template('login.html')

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
    # facilities = Facility.query.filter(Facility.availability == 'Yes')
    # for r in facilities:
    #     fac[r.facilityName] = r.facilityPropertyNumber

    sn = str(session.get("studentNumber"))
    page = request.args.get('page',1,type=int)
    reservations = Reservation.query.filter(Reservation.studentNumber == sn).order_by(Reservation.dateFrom.desc()).paginate(page=page,per_page=7)
    print(type(reservations))
    reservationss = Reservation.query.filter(Reservation.studentNumber == sn).order_by(Reservation.dateFrom.desc()).count()
    print(type(reservationss))
    # cur = mysql.connection.cursor()
    if reservations is None:
        msg = "No Reservations Found."
        return render_template('userDashboard.html', msg=msg)
    else:
        return render_template('userDashboard.html', reservations=reservations, reservationss=reservationss, form=form, equip=equip, fac=fac)

@app.route('/reservations')
@is_logged_in
def allReservations():
    page = request.args.get('page',1,type=int)
    reservations = Reservation.query.filter(Reservation.res_status == 'Active').order_by(Reservation.reservation_date.desc()).paginate(page=page,per_page=5)
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
    today = datetime.datetime.time(datetime.datetime.now())
    tod = today.strftime('%I:%M%p')
    if reservation.claimed_at == " ":
        reservation.claimed_at = tod
    else:
        reservation.returned_at = tod
    db.session.commit()

    return redirect(url_for('resDashboard'))

@app.route('/equipment/<int:equip_id>/delete',  methods=['POST','GET'])
@a_is_logged_in
def delete_equipment(equip_id):
    equipment = Equipment.query.get_or_404(equip_id)
    db.session.delete(equipment)
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

@app.route("/reservations/data", methods=['GET','POST'])
@a_is_logged_in
def getData():
    form = DateForm()
    if form.validate_on_submit():
        first = datetime.datetime.strptime(form.firstDate.data, '%Y-%m-%d').date()
        second = datetime.datetime.strptime(form.secondDate.data, '%Y-%m-%d').date()

        reservations = Reservation.query.filter(Reservation.dateFrom.between(str(first),str(second)))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        rendered = render_template('reservationData.html',reservations=reservations,first=first,second=second)
        pdf = pdfkit.from_string(rendered, False ,configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Reservations from '+str(first)+' to ' +str(second)+'.pdf'
        return response

    return render_template('filterReservations.html', form=form)

@app.route('/professors/data')
def prof():
    professors = Professor.query.all()

    profArray =[]

    for prof in professors:
        profObj = {}
        profObj['id'] = prof.id
        profObj['name'] = 'Prof. '+prof.firstName+' '+prof.lastName
        profArray.append(profObj)

    return jsonify({'professors' : profArray})

@app.route('/organizations/data')
def org():
    organizations = Organization.query.all()

    orgArray =[]

    for org in organizations:
        orgObj = {}
        orgObj['id'] = org.id
        orgObj['name'] = org.name
        orgArray.append(orgObj)

    return jsonify({'organizations' : orgArray})


if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()