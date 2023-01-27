from flask import current_app as app
#secure_filename is used to prevent malicious file uploads
from werkzeug.utils import secure_filename
import os
import uuid
from application.models import Orders
from application.database import db

def upload_file(file):
    
    
    #save the file to the upload folder
    filename = secure_filename(uuid.uuid4().hex + file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


#delete orders with given product id

def delete_order(product_id):
    orders = Orders.query.filter_by(product = product_id).all()
    for order in orders:
        print(order)
        if order.state=='cart':
            db.session.delete(order)
            db.session.commit()