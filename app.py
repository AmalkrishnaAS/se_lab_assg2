import os
from flask import Flask, session
from application import config
from application.config import DevelopConfig
from application.database import db

app=None
api=None

def create_app():
    app=Flask(__name__,template_folder="templates")
    print("Starting Development")
    app.config.from_object(DevelopConfig)
    db.init_app(app)
    app.app_context().push()
    return app,api

app,api=create_app()

from application.controllers import *

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)