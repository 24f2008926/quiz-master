from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db=SQLAlchemy()
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from app.models import create_admin
        db.create_all()
        create_admin()

    from app.routes import init_routes
    init_routes(app)

    return app