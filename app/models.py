from app import db
from werkzeug.security import generate_password_hash

# stores the subject data
class QZ_SUB_M(db.Model): 
    QZ_SUB_ID = db.Column(db.String(10), primary_key=True)
    QZ_SUB_NAME = db.Column(db.String(80), nullable=False, unique=True)
    QZ_SUB_DESC = db.Column(db.String(120))
    chapters = db.relationship('QZ_CHP_M', back_populates='subject', cascade='all, delete-orphan')

# stores the chapter data
class QZ_CHP_M(db.Model):  
    QZ_CHP_CHAP_ID = db.Column(db.String(10), primary_key=True)
    QZ_CHP_NAME = db.Column(db.String(80), nullable=False)
    QZ_CHP_DESC = db.Column(db.String(120))
    QZ_CHP_SUB_ID = db.Column(db.String(10), db.ForeignKey('qz_sub_m.QZ_SUB_ID'), nullable=False)

    subject = db.relationship('QZ_SUB_M', back_populates='chapters')
    quizzes = db.relationship('QZ_QIZ_HDR', back_populates='chapter', cascade='all, delete-orphan')

# stores the quiz data
class QZ_QIZ_HDR(db.Model): 
    QZ_QIZ_QUIZ_ID = db.Column(db.String(10), primary_key=True)
    QZ_QIZ_QUIZ_NAME = db.Column(db.String(255), nullable=False)
    QZ_QIZ_DOC = db.Column(db.Date)
    QZ_QIZ_DUR = db.Column(db.Time)
    QZ_QIZ_DESC = db.Column(db.String(500))
    QZ_QIZ_MAX = db.Column(db.Integer)
    QZ_QIZ_SUB_ID = db.Column(db.String(10), db.ForeignKey('qz_sub_m.QZ_SUB_ID'), nullable=False)
    QZ_QIZ_CHAP_ID = db.Column(db.String(10), db.ForeignKey('qz_chp_m.QZ_CHP_CHAP_ID'), nullable=False)

    subject = db.relationship('QZ_SUB_M')
    chapter = db.relationship('QZ_CHP_M', back_populates='quizzes')
    questions = db.relationship('QZ_QTN_DET', back_populates='quiz', cascade='all, delete-orphan')

# stores the questions along with options
class QZ_QTN_DET(db.Model):
    QZ_QTN_ID = db.Column(db.String(10), primary_key=True)
    QZ_QTN_QUZ_ID = db.Column(db.String(10), db.ForeignKey('qz_qiz_hdr.QZ_QIZ_QUIZ_ID'), nullable=False)
    QZ_QTN_QUZ_DET= db.Column(db.String(255))
    QZ_QTN_QTN_OPT_1 = db.Column(db.String(255))
    QZ_QTN_QTN_OPT_2 = db.Column(db.String(255))
    QZ_QTN_QTN_OPT_3 = db.Column(db.String(255))
    QZ_QTN_QTN_OPT_4 = db.Column(db.String(255))
    QZ_QTN_QTN_COR_OP = db.Column(db.String(255))

    quiz = db.relationship('QZ_QIZ_HDR', back_populates='questions')

# stores the user data
class QZ_USR_M(db.Model): 
    QZ_USR_USER_ID = db.Column(db.String(10), primary_key=True)
    QZ_USR_USERNAME = db.Column(db.String(255), nullable=False)
    QZ_USR_EMAIL = db.Column(db.String(255), nullable=False)
    QZ_USR_PASSWORD = db.Column(db.String(255), nullable=False)
    QZ_USR_DOB = db.Column(db.Date)
    QZ_USR_QUAL = db.Column(db.String(255))
    QZ_USR_ROLE=db.Column(db.String(5),default='user')

# stores previous attempt
class QZ_ATM_HDR(db.Model): 
    QZ_ATM_ATMT_ID = db.Column(db.String(10), primary_key=True)
    QZ_ATM_QUIZ_ID = db.Column(db.String(10), db.ForeignKey('qz_qiz_hdr.QZ_QIZ_QUIZ_ID'), nullable=False)
    QZ_ATM_USER_ID = db.Column(db.String(10), db.ForeignKey('qz_usr_m.QZ_USR_USER_ID'), nullable=False)
    QZ_ATM_TIME = db.Column(db.Time)
    QZ_ATM_SCORE = db.Column(db.Integer)
    QZ_ATM_DATE = db.Column(db.DateTime)
    QZ_ATM_CO = db.Column(db.Integer)
    QZ_ATM_INCO = db.Column(db.Integer)

    user = db.relationship('QZ_USR_M')
    quiz = db.relationship('QZ_QIZ_HDR')



# function to create a admin if does not exist
def create_admin():
    if not QZ_USR_M.query.filter_by(QZ_USR_USERNAME="admin").first():
        admin = QZ_USR_M(
            QZ_USR_USER_ID="admin001",
            QZ_USR_USERNAME="admin",
            QZ_USR_EMAIL="admin@example.com",
            QZ_USR_PASSWORD=generate_password_hash("admin123"),
            QZ_USR_ROLE="admin")
        db.session.add(admin)
        db.session.commit()
