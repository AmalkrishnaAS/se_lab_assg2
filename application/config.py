import os

basedir=os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG=False
    SQLITE_DB_DIR=None
    SQLALCHEMY_DATABASE_URI=None
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY=None
    
class DevelopConfig(Config):
    SQLITE_DB_DIR=os.path.join(basedir,"../db_directory/")
    SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(SQLITE_DB_DIR,"appdb.sqlite3")
    DEBUG=True
    SECRET_KEY="fgdmgfdgnmddrmdfmngndsm"
    SESSION_PERMANENT=False
    SESSION_TYPE="filesystem"
    UPLOAD_FOLDER=os.path.join(basedir,"../static/uploads/")
    ALLOWED_EXTENSIONS=set(["png","jpg","jpeg","gif"])
    STATIC_FOLDER=os.path.join(basedir,"../static/")