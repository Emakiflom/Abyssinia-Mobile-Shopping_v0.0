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

config = {
  "apiKey": "AIzaSyDWaWvTMA563HJpopkVDXah0m-P-iDNcM0",
  "authDomain": "absiniyamobile.firebaseapp.com",
  "projectId": "absiniyamobile",
  "storageBucket": "absiniyamobile.appspot.com",
  "databaseURL": "https://absiniyamobile.firebaseio.com",
  "messagingSenderId": "847444916101",
  "appId": "1:847444916101:web:e5d56f76242de8b4c9f6ec",
  "measurementId": "G-40BMPNTXV2"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


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
    price = db.Column(db.Double, nullable=False)
    category = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)

# Handle registration form submission and insert data into the database

@app.route('/')
def home():
    admin_true = session.get('admin_true')
    items = Item.query.all()
    return render_template('home.html', items=items, admin_true = admin_true)


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
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
            new_user = Users(FirstName=first_name, LastName=last_name, Email=email, Password=password, Address=address, PhoneNumber=phone_number)
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

# Define the profile route to display the profile.html page
@app.route('/view_item')
def view_item():
    items = Item.query.all()
    admin_true = session.get('admin_true')
    return render_template('view_item.html', items=items, admin_true = admin_true)

@app.route("/view_item_detail/<int:item_id>")
def view_item_detail(item_id):
    item = Item.query.filter_by(item_id=item_id).first()
    if item:
        return render_template("view_item_detail.html", items=item)
    else:
        return "Item not found."


@app.route('/add_item', methods=['GET','POST'])
def add_item():
    if request.method == 'POST':
        
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        unique_combination = generate_random_combination()
        detail = request.form['detail']

        upload = request.files['image']
        storage.child("images/"+unique_combination+".jpg").put(upload)

        get_pic_url = storage.child("images/"+unique_combination+".jpg").get_url(None)

        # Create a new Item object
        new_item = Item(
            name=name,
            price=price,
            category=category,
            image=get_pic_url,
            details=detail
        )

        print(get_pic_url)
        db.session.add(new_item)
        db.session.commit()
        
        return redirect(url_for('home'))
    
    
    return render_template('register_item.html')

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    
    item = Item.query.filter_by(item_id=item_id).first()
    if item:
        return render_template("edit_item.html", item=item)
    else:
        return "Item not found."
    
@app.route('/edit', methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        
        item_id = request.form['item_id']
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        unique_combination = generate_random_combination()
        detail = request.form['detail']
        image_url = request.form['image_url']
        
      
      
        file = request.files['image']

        if file:
            upload = request.files['image']
            storage.child("images/"+unique_combination+".jpg").put(upload)
            image_url = storage.child("images/"+unique_combination+".jpg").get_url(None)

        # Query the item
        item_to_update = Item.query.get(item_id)


        if item_to_update:
         # Update the attributes
         item_to_update.name = name
         item_to_update.price = price
         item_to_update.category = category
         item_to_update.image = image_url
         item_to_update.details = detail

         # Commit the changes to the database
         db.session.commit()
        else:
            print("Item not found")

        return redirect(url_for('view_item'))
    
    
    return render_template('edit_item.html')

@app.route("/delete_item/<int:item_id>")
def delete_item(item_id):

    item = Item.query.filter_by(item_id=item_id).first()
    if item:
        return render_template("delete_item.html", items=item)
    else:
        return "Item not found."



@app.route('/drop_item', methods=['GET','POST'])
def drop_item():
    if request.method == 'POST':
        
        item_id = request.form['item_id']
        # Query the item
        item_to_delete = Item.query.get(item_id)

        if item_to_delete:
        # Mark the item for deletion
         db.session.delete(item_to_delete)

        # Commit the session to persist the changes to the database
         db.session.commit()
        
        return redirect(url_for('view_item'))
    
    
    return render_template('view_item.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))