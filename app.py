from flask import Flask, render_template, redirect, url_for, flash, request ,session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyrebase
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define your MySQL database connection parameters
db_config = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "piyasa_dev_db",
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root@localhost/absiniya?unix_socket=/opt/lampp/var/mysql/mysql.sock'
db = SQLAlchemy(app)

def generate_random_combination():
    characters = string.ascii_lowercase
    return ''.join(random.choice(characters) for _ in range(6))
# Define a User model for the database
# class User(db.Model):
#     UserID = db.Column(db.Integer, primary_key=True)
#     FirstName = db.Column(db.String(20), nullable=False)
#     LastName = db.Column(db.String(20), nullable=False)
#     Email = db.Column(db.String(45), unique=True, nullable=False)
#     Password = db.Column(db.String(128), nullable=False)
#     Address = db.Column(db.String(45), nullable=False)
#     PhoneNumber = db.Column(db.String(20), nullable=False)

class Users(db.Model):
    users_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(45), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False) 
    password = db.Column(db.String(128), nullable=False)

#Define an Item model for the database
class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    reg_date = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

# Handle registration form submission and insert data into the database

@app.route('/')
def home():
    admin_true = session.get('admin_true')
    items = Item.query.all()
    return render_template('home.html', items=items, admin_true = admin_true)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phoneNumber']

        # Check if the email is already registered
        if Users.query.filter_by(Email=email).first():
            flash('Email already registered!', 'error')
        else:
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(password, method='sha256')
            
            # Create a new user instance and add it to the database
            new_user = Users(FirstName=first_name, LastName=last_name, Email=email, Password=hashed_password, Address=address, PhoneNumber=phone_number)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))

    return render_template('register.html')

# Handle login form submission and check user credentials in the database
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if a user with the provided username or email exists
        #user = Users.query.filter((Users.email == username) | (Users.FirstName == username)).first()
        user = Users.query.filter((Users.email == username)).first()

        if_admin_ture= user.admin

        

        #if user and check_password_hash(user.Password, password):
        if user and user.password:
            flash('Login successful!', 'success')
            # Redirect to the profile page upon successful login
            session['admin_true'] = if_admin_ture
            return redirect(url_for('profile'))

        flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


# Define the profile route to display the profile.html page
@app.route('/profile')
def profile():
    admin_true = session.get('admin_true')
    items = Item.query.all()
    return render_template('profile.html', items=items, admin_true = admin_true)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))