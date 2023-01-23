from application.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(10), nullable=False)


class Vendors(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    
class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    vendor = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    qty = db.Column(db.Numeric(10,2), nullable=False)
    unit = db.Column(db.String(255), nullable=False)

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    qty = db.Column(db.Numeric(10,2), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    state = db.Column(db.String(255), nullable=False)