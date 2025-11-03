from flask import Flask, flash, redirect, render_template, request, session, url_for    
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
import MySQLdb
# from functools import wraps # not used currently but can be useful for decorators

app = Flask(__name__)

# my sql configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key'
 
mysql = MySQL(app)  

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()]) 
    credits = StringField('Credits', validators=[DataRequired()])   
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/',methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        course = form.course.data
        credits = form.credits.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # <-- FIXED!
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('login'))
        
        cursor.execute('INSERT INTO user (name, email, password, course, credits) VALUES (%s, %s, %s, %s, %s)', 
                       (name, email, password, course, credits))
        mysql.connection.commit()
        cursor.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # <-- FIXED!
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        # think of session as a temporary storage for user data during their visit
        if user and password == user['password']:
            session['logged_in'] = True
            session['user_id'] = user['id']
            # checking if the user loggin in is admin or not
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            # now the user is redirected to different pages based on their role
            if session['is_admin'] == 1:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

# In the context of the if not session.get('logged_in') check, 
# a None return value (when the key is missing) evaluates to False in Python, 
# which correctly triggers the unauthorized access logic without breaking the application.
# we didnot use simple session['logged_in'] because if the key 'logged_in' doesnot exist in session dictionary it will throw an error
# The get method of session returns None if the key is not found, which is treated as False in a boolean context.
@app.route('/admin_dashboard')
def admin_dashboard():  
    if not session.get('logged_in') or session.get('is_admin') != 1:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    # grabing all users from database to show in admin dashboard
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # <-- FIXED
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        cursor.close()
        return render_template('admin_dashboard.html', users=users)

@app.route('/GCS1')
def home():
    return render_template('GCS1.html')

if __name__ == '__main__':
    app.run(debug=True)            
