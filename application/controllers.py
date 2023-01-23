from flask import request, redirect, render_template, url_for, flash, session
import re
from passlib.hash import sha256_crypt
from functools import wraps

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
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        phone = request.form['phone']
        category = request.form.get('User')
        
        if category == 'Buyer':
            if email.split('@')[1] != "nitc.ac.in":
                flash('Enter a Valid NITC Mail ID','danger')
                return redirect(url_for('register'))
            user = User(name=name, email=email, password=password, phone=phone)
            db.session.add(user)
            db.session.commit()
            flash('User Registered Successfully','success')
            return redirect(url_for('login'))
        
        elif category == 'Vendor':
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
    return render_template('buyer_home.html',user = session['username'])

@app.route('/cart')
@buyer_login_required
def cart():
    return "cart"

@app.route('/orders')
@buyer_login_required
def orders():
    return "cart"


@app.route('/vendor/home')
@vendor_login_required
def vendor_home():
    return render_template('vendor_home.html',user = session['username'])

@app.route('/vendor/orders')
@vendor_login_required
def vendor_orders():
    return render_template('vendor_orders.html')

@app.route('/vendor/past_orders')
@vendor_login_required
def vendor_past_orders():
    return render_template('vendor_past_orders.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')