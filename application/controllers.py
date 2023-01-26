from flask import request, redirect, render_template, url_for, flash, session
import re
from passlib.hash import sha256_crypt
from functools import wraps
from flask_session import Session

from flask import current_app as app

from application.models import *

def buyer_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'type' in session and session['type'] == 'Buyer' and 'status' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Access','danger')
            return redirect(url_for('login'))
    return wrap

def vendor_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'type' in session and session['type'] == 'Vendor' and 'status' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Access','danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def main():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        
        if request.form.get('User') == 'Buyer':
            user = User.query.filter_by(email=email).first()
        elif request.form.get('User') == 'Vendor':
            user = Vendors.query.filter_by(email=email).first()
        else:
            user = None

        if user is None:
            flash('Non Existent User','danger')
            return redirect(url_for('login'))
        
        if sha256_crypt.verify(password,user.password):
            session['status'] = True
            session['type'] = request.form['User']
            session['username'] = user.name
            session['id']=user.id
            
            flash('User Logged In','success')
            if request.form['User'] == 'Vendor':
                return redirect(url_for('vendor_home'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid Password','danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
      if request.form['password']!= request.form['confirm']:
         flash('passwords not matching','danger')
         return render_template('register.html')
      
      else:
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        phone = request.form['phone']
        category = request.form.get('User')
        
        if category == 'Buyer':
            user = User.query.filter_by(email=email).first()
            if user is not None:
                flash('Existing User','danger')
                return redirect(url_for('register'))
            if email.split('@')[1] != "nitc.ac.in":
                flash('Enter a Valid NITC Mail ID','danger')
                return render_template('register.html')
            user = User(name=name, email=email, password=password, phone=phone)
            db.session.add(user)
            db.session.commit()
            flash('User Registered Successfully','success')
            return redirect(url_for('login'))
        
        elif category == 'Vendor':
            user = Vendors.query.filter_by(email=email).first()
            if user is not None:
                flash('Existing User','danger')
                return redirect(url_for('register'))
            vendor = Vendors(name=name, email=email, password=password, phone=phone)
            db.session.add(vendor)
            db.session.commit()
            flash('Vendor Registered Successfully','success')
            return redirect(url_for('login'))
        
        else:
            flash('Enter type of User','danger')
            return redirect(url_for('register'))
        
    else:
        return render_template('register.html')
    
@app.route('/home')
@buyer_login_required
def home():
    products=Products.query.all()
    vendors=[]
    for product in products:
        vendor=Vendors.query.with_entities(Vendors.name).filter_by(id=product.vendor).first()
        vendors.append(vendor)
    return render_template('buyer_home.html',user = session['username'],products=products, vendors=vendors)

@app.route('/cart')
@buyer_login_required
def cart():
    return "cart"

@app.route('/orders')
@buyer_login_required
def orders():
    id=session['id']
    # print(id)
    # here we get all the orders from user with given id
    orders=Orders.query.filter_by(user=id).all()
    # here we are defining 2 lists to store the vendor and product details of the orders
    vendors=[]
    products=[]
    # here we are iterating through the orders and getting the vendor and product details of each order
    for order in orders:
        vendor=Vendors.query.filter_by(id=order.vendor).first()
        vendors.append(vendor)
        product=Products.query.filter_by(id=order.product).first()
        products.append(product)
    return render_template('buyer_orders.html', orders=orders, vendors=vendors, products=products)


@app.route('/vendor/home')
@vendor_login_required
def vendor_home():
    products=[]
    # here we get all the products from vendor with given id
    id=session['id']
    products=Products.query.filter_by(vendor=id).all()
    return render_template('vendor_home.html',user = session['username'], products=products)

@app.route('/vendor/orders')
@vendor_login_required
def vendor_orders():
    id=session['id']
    # here we get all the orders from vendor with given id
    orders=Orders.query.filter_by(vendor=id, state="processing").all()
    customers=[]
    products=[]
    units=[]
    # here we are iterating through the orders and getting the customer and product details of each order
    for order in orders:
        customer=User.query.filter_by(id=order.user).first()
        customers.append(customer.name)
        product=Products.query.filter_by(id=order.product).first()
        products.append(product.name)
        units.append(product.unit)
    return render_template('vendor_orders.html', orders=orders, customers=customers, products=products, units=units)

@app.route('/vendor/past_orders')
@vendor_login_required
def vendor_past_orders():
    id=session['id']
    # here we get all the orders from vendor with given id and already delivered
    orders=Orders.query.filter_by(vendor=id, state="delivered").all()
    customers=[]
    products=[]
    units=[]

    # here we are iterating through the orders and getting the customer and product details of each order
    for order in orders:
        customer=User.query.filter_by(id=order.user).first()
        customers.append(customer.name)
        product=Products.query.filter_by(id=order.product).first()
        products.append(product.name)
        units.append(product.unit)
    return render_template('vendor_past_orders.html', orders=orders, customers=customers, products=products, units=units)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')