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
from sqlalchemy.orm import aliased

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
#Define a Cart model for the database
class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'), nullable=False)
    cart_status = db.Column(db.String(45), unique=True, nullable=False)
     # Define the relationship to Item
    item = db.relationship('Item', back_populates='carts')

class Users(db.Model):
    users_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(45), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False) 
    password = db.Column(db.String(128), nullable=False)

class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(20), nullable=False)
    contact_message = db.Column(db.String(230), nullable=False)

#Define an Item model for the database
class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Double, nullable=False)
    category = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    carts = db.relationship('Cart', back_populates='item')



# Handle registration form submission and insert data into the database

@app.route('/')
def home():
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
    items = Item.query.all()

    if admin_true:
        return render_template('home.html', items=items, admin_true = admin_true)
    else:
        return render_template('home.html', items=items, admin_true = admin_true, user_id = user_id)



@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']

        # Check if the email is already registered
        if Users.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
        else:
            # Hash the password before storing it in the database
            #hashed_password = generate_password_hash(password, method='sha256')
            
            # Create a new user instance and add it to the database
            new_user = Users(name=name, email=email, password=password, address=address, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))

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
        user_id = user.users_id
        name_get = user.name

    
        #if user and check_password_hash(user.Password, password):
        if user and user.password:
            flash('Login successful!', 'success')
            # Redirect to the profile page upon successful login
            session['admin_true'] = if_admin_ture
            session['user_id'] = user_id
            session['name_get'] = name_get
            if if_admin_ture:
                return redirect(url_for('view_item'))
            else:
                return redirect(url_for('profile'))

        flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


# Define the profile route to display the profile.html page
@app.route('/profile')
def profile():
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
    name_get = session.get('name_get')
    items = Item.query.all()
    return render_template('profile.html', items=items, admin_true = admin_true, user_id = user_id, name_get= name_get)

# Define the profile route to display the profile.html page
@app.route('/view_item')
def view_item():
    items = Item.query.all()
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
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

@app.route('/add_cart', methods=['GET','POST'])
def add_cart():
    if request.method == 'POST':
        
        item_id = request.form['item_id']
        user_id = session.get('user_id')
        cart_status = '0'


        # Create a new Item object
        new_item = Cart(
            user_id=user_id,
            item_id=item_id,
            cart_status = cart_status
        )

        db.session.add(new_item)
        db.session.commit()
        
        return redirect(url_for('view_cart'))
    
    
    return render_template('cart.html')


# Define the profile route to display the profile.html page
@app.route('/view_cart')
def view_cart():
    user_id = session.get('user_id')
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
    name_get = session.get('name_get')
    
    cart_items = db.session.query(Cart, Item).join(Item, Cart.item_id == Item.item_id).filter(Cart.user_id == user_id).all()


    return render_template('view_cart.html', cart_items=cart_items, admin_true = admin_true, user_id = user_id, name_get= name_get)


@app.route('/remove_cart', methods=['GET','POST'])
def remove_cart():
    if request.method == 'POST':
        
        cart_id = request.form['cart_id']
        # Query the item
        cart_to_delete = Cart.query.get(cart_id)

        if cart_to_delete:
        # Mark the item for deletion
         db.session.delete(cart_to_delete)

        # Commit the session to persist the changes to the database
         db.session.commit()
        
        return redirect(url_for('view_cart'))
    
    
    return render_template('view_cart.html')

# Define the Contact route to display the contact.html page
@app.route('/contact')
def contact():
    items = Item.query.all()
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
    return render_template('contact.html', items=items, admin_true = admin_true, user_id = user_id)

@app.route('/add_contact', methods=['GET','POST'])
def add_contact():
    flash('This is a toast message!')
    if request.method == 'POST':
        
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash('Your message has been sent successfully!', 'success')

        # Create a new Contact object
        new_item = Contact(
            contact_name=name,
            contact_email=email,
            contact_message=message
        )

        db.session.add(new_item)
        db.session.commit()
        
        return redirect(url_for('contact'))

    return render_template('contact.html')


# Define the about route to display the about.html page
@app.route('/about')
def about():
    items = Item.query.all()
    admin_true = session.get('admin_true')
    user_id = session.get('user_id')
    return render_template('about.html', items=items, admin_true = admin_true, user_id = user_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))