from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from app.models import QZ_SUB_M,QZ_CHP_M,QZ_QIZ_HDR,QZ_QTN_DET,QZ_ATM_HDR,QZ_USR_M
        db.create_all()  

    return app
