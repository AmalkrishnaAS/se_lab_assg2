from application.models import *
from flask import current_app as app

def not_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() not in app.config['ALLOWED_EXTENSIONS']


def format_filename(id,filename):
    ext = filename.rsplit('.', 1)[1].lower()
    new_name = str(id) + '.' + ext
    return new_name

def get_product_list(products):
    product_list = []
    for product in products:
        vendor = Vendors.query.filter(Vendors.id==product.vendor).first()
        product_list.append({
            'id': product.id,
            'name': product.name,
            'vendor': vendor.name,
            'price': product.price,
            'qty' : product.qty,
            'unit': product.unit,
            'image': product.image
        })
    
    return product_list

def get_cart_data(id):
    cart_list = []
    orders = Orders.query.filter_by(user=id,state="In Cart").all()
    for order in orders:
        product = Products.query.filter_by(id=order.product).first()
        vendor = Vendors.query.filter_by(id=order.vendor).first()
        cart_list.append({
            'id': order.id,
            'image': product.image,
            'name': product.name,
            'qty' : order.qty,
            'vendor': vendor.name,
            'price': product.price,
            'available': product.qty,
            'unit': product.unit,
            'total': round(product.price*order.qty,2)
        })
    return cart_list

def get_orders(id):
    orders = Orders.query.filter_by(user=id).order_by(Orders.date.desc()).all()
    current_orders = []
    past_orders = []
    for order in orders:
        product = Products.query.filter_by(id=order.product).first()
        vendor = Vendors.query.filter_by(id=order.vendor).first()
        item = {
            'vendor_name': vendor.name,
            'vendor_phone': vendor.phone,
            'product_name': product.name,
            'qty': order.qty,
            'date': order.date,
            'price': round(order.price * order.qty,2)
        }
        if order.state == "Ordered":
            current_orders.append(item)
        elif order.state == "Delivered":
            past_orders.append(item)
    return current_orders,past_orders

def get_vendor_orders(orders):
    out = []
    for order in orders:
        product = Products.query.filter_by(id=order.product).first()
        buyer = User.query.filter_by(id=order.user).first()
        item = {
            'id': order.id,
            'buyer_name': buyer.name,
            'buyer_phone': buyer.phone,
            'product_name': product.name,
            'qty': order.qty,
            'date': order.date,
            'price': round(order.price * order.qty,2)
        }
        out.append(item)
    return out

def get_customers(id):
    orders = Orders.query.distinct(Orders.user).with_entities(Orders.user).filter_by(vendor=id, state="Ordered").all()
    out = []
    for order in orders:
        item = User.query.filter_by(id=order.user).first()
        out.append(item)
    return out