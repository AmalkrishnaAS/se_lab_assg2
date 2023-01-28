import os
from flask import request, redirect, render_template, url_for, flash, session
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime

from flask import current_app as app

from application.models import *
from application import utils

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
        
        #check if existing user
        if request.form.get('User') == 'Buyer':
            user = User.query.filter_by(email=email).first()
        elif request.form.get('User') == 'Vendor':
            user = Vendors.query.filter_by(email=email).first()
        else:
            user = None

        if user is None:
            flash('Non Existent User','danger')
            return redirect(url_for('login'))
        
        #verify Password
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
        #check confirm password
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
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
    
@app.route('/home',methods=["GET",'POST'])
@buyer_login_required
def home():
    products = Products.query.all()
    if request.method == "POST":
        print(request.form['vendor'],request.form['category'])
        if request.form['vendor'] != "Select Vendor" and request.form['category'] != "Select Category":
            products = Products.query.filter_by(vendor=request.form['vendor'],category=request.form['category']).all()
        elif request.form['vendor'] != "Select Vendor":
            products = Products.query.filter_by(vendor=request.form['vendor']).all()
        elif request.form['category'] != "Select Category":
            products = Products.query.filter_by(category=request.form['category']).all()
    product_list = utils.get_product_list(products)
    vendors = Vendors.query.all()
    return render_template('buyer_home.html',user = session['username'],products = product_list,vendors = vendors)

@app.route('/add/<int:id>/cart',methods=["POST"])
@buyer_login_required
def add_to_cart(id):
    qty = request.form['quantity']
    product = Products.query.filter_by(id=id).first()
    if float(qty)==0:
        flash("Enter a Valid Quantity",'warning')
        return redirect(url_for('home'))
    if product.qty < float(qty):
        flash("Requested Quantity Not Available",'danger')
        return redirect(url_for('home'))
    order = Orders(vendor = product.vendor,
                   user = session['id'],
                   product = product.id,
                   date = datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                   qty = qty,
                   price = product.price,
                   state = "In Cart"
                   )
    db.session.add(order)
    db.session.commit()
    flash("Added to Cart",'success')
    return redirect(url_for('home'))

@app.route('/cart')
@buyer_login_required
def cart():
    items = utils.get_cart_data(session['id'])
    return render_template("cart.html",orders=items)

@app.route('/order/<int:id>/delete')
@buyer_login_required
def delete_from_kart(id):
    order = Orders.query.filter_by(id=id).first()
    if order.user!= session['id']:
        flash('Unauthorized Access','danger')
        return redirect(url_for('login'))
    db.session.delete(order)
    db.session.commit()
    flash('Item Removed from Cart','success')
    return redirect(url_for('cart'))

@app.route('/order/<int:id>/edit',methods=['GET','POST'])
@buyer_login_required
def edit_kart(id):
    order = Orders.query.filter_by(id=id).first()
    if order.user!= session['id']:
        flash('Unauthorized Access','danger')
        return redirect(url_for('login'))
    product = Products.query.filter_by(id=order.product).first()
    if request.method == 'POST':
        qty = request.form['qty']
        if float(qty) > product.qty:
            flash("Requested Quantity Not Available",'danger')
            return redirect(url_for('cart'))
        else:
            order.qty = qty
            db.session.commit()
            flash("Order Updated",'success')
            return redirect(url_for('cart'))
    else:
        vendor = Vendors.query.filter_by(id=order.vendor).first()
        return render_template('edit_order.html',order = order, product = product,vendor=vendor)



@app.route('/add/<int:id>/order')
@buyer_login_required
def item_order(id):
    order = Orders.query.filter_by(id=id).first()
    if order.user != session['id']:
        flash('Unauthorized Access','danger')
        return redirect(url_for('login'))
    product = Products.query.filter_by(id=order.product).first()
    if order.qty > product.qty:
        flash("Requested Quantity Not Available",'danger')
        return redirect(url_for('cart'))
    else:
        order.state = "Ordered"
        order.price = product.price
        order.date = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        product.qty = product.qty - order.qty
        db.session.commit()
        flash("Order Placed",'success')
        return redirect(url_for('cart'))
        

@app.route('/orders')
@buyer_login_required
def orders():
    orders, prev_orders = utils.get_orders(session['id'])
    return render_template('orders.html', orders=orders, prev_orders = prev_orders )


@app.route('/vendor/home')
@vendor_login_required
def vendor_home():
    products=Products.query.filter_by(vendor=session['id']).all()
    return render_template('vendor_home.html',user = session['username'], products=products)

@app.route('/vendor/orders',methods=["GET","POST"])
@vendor_login_required
def vendor_orders():
    orders=Orders.query.filter_by(vendor=session['id'], state="Ordered").all()
    if request.method == "POST":
        if request.form['customer'] != "Select Customer":
            orders=Orders.query.filter_by(vendor=session['id'],user=request.form['customer'], state="Ordered").all()
    orders= utils.get_vendor_orders(orders)
    customers = utils.get_customers(session['id'])
    return render_template('vendor_orders.html', orders = orders, customers =customers)

@app.route('/order/<int:id>/delivery')
@vendor_login_required
def delivered(id):
    order=Orders.query.filter_by(id=id).first()
    if order.vendor!= session['id']:
        flash('Unauthorized Access','danger')
        return redirect(url_for('login'))
    order.state = "Delivered"
    db.session.commit()
    return redirect(url_for('vendor_orders'))

@app.route('/vendor/past_orders')
@vendor_login_required
def vendor_past_orders():
    orders=Orders.query.filter_by(vendor=session['id'], state="Delivered").all()
    orders= utils.get_vendor_orders(orders)
    return render_template('vendor_past_orders.html', orders = orders)

@app.route('/product/add',methods=['GET','POST'])
@vendor_login_required
def add_product():
    if request.method=='POST':
        name = request.form['product_name']
        category = request.form['category']
        qty = request.form['qty']
        unit = request.form['unit']
        if unit=="None" and float(qty)!=float(qty)//1:
            flash("Unit Required for Fractional Quantity",'danger')
            return redirect(url_for('add_product'))
        if unit == "None":
            unit = ' '
        price = request.form['price']
        vendor = session['id'] 
        image = request.files['image']
            
        if utils.not_allowed_file(image.filename):
            flash("invalid file type", "danger")
            return redirect(url_for('add_product.html'))

        product = Products(name = name,
                           vendor = vendor,
                           category = category,
                           price = price,
                           qty = qty,
                           unit = unit,
                           image = 'Hello')
        
        db.session.add(product)
        db.session.commit()
        
        product_new = Products.query.filter_by(image='Hello',vendor=vendor).first()
        filename = secure_filename(utils.format_filename(product_new.id,image.filename))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        product_new.image = filename
        db.session.commit()
        
        flash('New Product Added','success')
        return redirect(url_for('vendor_home'))      
        
    return render_template('add_product.html')

@app.route('/product/<int:id>/edit',methods=['GET','POST'])
@vendor_login_required
def edit_product(id):
    product = Products.query.filter_by(id=id).first()
    if product.vendor!= session['id']:
        flash('Unauthorized Access','danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        product.name = request.form['product_name']
        product.category = request.form['category']
        product.qty = request.form['qty']
        unit = request.form['unit']
        if unit=="None" and float(product.qty)!=float(product.qty)//1:
            flash("Unit Required for Fractional Quantity",'danger')
            return redirect(url_for('edit_product',id=id))
        if unit == "None":
            product.unit = ' '
        else:
            product.unit = unit
        product.price = request.form['price']
        product.vendor = session['id']
        image = request.files.get('image')
        if utils.not_allowed_file(image.filename):
            flash("invalid file type", "danger")
            return redirect(url_for('edit_product',id=id))
        if image.filename:
            path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
            os.remove(path)
            image.save(path)
            
        db.session.commit()
        
        flash('Product Edited','success')
        return redirect(url_for('vendor_home')) 
        
    else:
        return render_template('edit_product.html',product=product)