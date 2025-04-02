class Config:
    SECRET_KEY = "Gokul"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
