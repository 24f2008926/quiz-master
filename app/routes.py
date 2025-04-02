from flask import render_template, request, redirect, url_for, session,flash
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import QZ_USR_M, QZ_SUB_M, QZ_CHP_M,QZ_QIZ_HDR,QZ_ATM_HDR,QZ_QTN_DET
import uuid
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from flask import Flask, render_template
from app import db
from sqlalchemy import desc,func

def init_routes(app):
    
    #home route
    @app.route('/')
    def home():
        return render_template('home.html')
    
    #login route
    @app.route('/login',methods=['GET','POST'])
    def login():
        if request.method=='POST':
            username= request.form['username']
            password= request.form['password']
            user= QZ_USR_M.query.filter_by(QZ_USR_USERNAME=username).first()
            if user and check_password_hash(user.QZ_USR_PASSWORD,password):
                session['user_id']=user.QZ_USR_USER_ID
                session['username']= user.QZ_USR_USERNAME
                session['role']=user.QZ_USR_ROLE
                return redirect(url_for('dashboard'))
            
        return render_template('login.html')
    

    #logout route
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))
    

    # reoute to veiw the past results
    @app.route('/past_results/<string:quiz_id>')
    def past_results(quiz_id):
        user_id= session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        
        results= QZ_ATM_HDR.query.filter_by(QZ_ATM_USER_ID=user_id, QZ_ATM_QUIZ_ID=quiz_id).order_by(QZ_ATM_HDR.QZ_ATM_DATE.desc()).all()

        return render_template('past_results.html',results=results)
    
    #register route
    @app.route('/register',methods=['GET','POST'])
    def register():
        if request.method=='POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            if QZ_USR_M.query.filter_by(QZ_USR_USERNAME=username).first():
                return redirect(url_for('login'))
            
            user_id=str(uuid.uuid4())[:10]
            hashed_password = generate_password_hash(password)

            new_user= QZ_USR_M(QZ_USR_USER_ID=user_id, QZ_USR_USERNAME=username, QZ_USR_EMAIL=email, QZ_USR_PASSWORD=hashed_password, QZ_USR_ROLE="user")

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))
        
        return render_template('register.html')
    

    # route to add new subject
    @app.route('/add_subject', methods=['GET', 'POST'])
    def add_subject():
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))

        if request.method == 'POST':
            subject_name = request.form['subject_name']
            subject_desc = request.form['subject_description']

            if QZ_SUB_M.query.filter_by(QZ_SUB_NAME=subject_name).first():
                return redirect(url_for('add_subject'))

            subject_id = str(uuid.uuid4())[:10]
            new_subject = QZ_SUB_M(QZ_SUB_ID=subject_id, QZ_SUB_NAME=subject_name, QZ_SUB_DESC=subject_desc)

            db.session.add(new_subject)
            db.session.commit()

            return redirect(url_for('dashboard'))

        return render_template('add_subject.html')
    

    # route to veiw the subjects
    @app.route('/subject/<subject_id>')
    def view_subject(subject_id):
        subject = QZ_SUB_M.query.get_or_404(subject_id)
        chapters = QZ_CHP_M.query.filter_by(QZ_CHP_SUB_ID=subject_id).all()
        return render_template('view_subject.html', subject=subject, chapters=chapters)
    

    # dashboard displays all the subjects
    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        if 'username' not in session:
            return redirect(url_for('login'))

        search_query = request.args.get('search', '').strip()
        
        if search_query:
            subjects = QZ_SUB_M.query.filter(QZ_SUB_M.QZ_SUB_NAME.ilike(f"%{search_query}%")).all()
        else:
            subjects = QZ_SUB_M.query.all()

        return render_template('dashboard.html', subjects=subjects)
    

    # route to add a chapter
    @app.route('/add_chapter/<subject_id>',methods=['GET','POST'])
    def add_chapter(subject_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        if request.method=='POST':
            chapter_name=request.form['chapter_name']
            chapter_desc = request.form['chapter_description']
            if QZ_CHP_M.query.filter_by(QZ_CHP_NAME=chapter_name, QZ_CHP_SUB_ID=subject_id).first():
               return redirect(url_for('add_chapter', subject_id=subject_id))
            chapter_id=str(uuid.uuid4())[:10]
            new_chapter =  QZ_CHP_M(QZ_CHP_CHAP_ID=chapter_id, QZ_CHP_NAME=chapter_name, QZ_CHP_DESC=chapter_desc, QZ_CHP_SUB_ID=subject_id)
            db.session.add(new_chapter)
            db.session.commit()

            return redirect(url_for('view_subject', subject_id=subject_id))
        return render_template('add_chapter.html',subject_id=subject_id)
    
    # route to view quizzes in a chapter
    @app.route('/chapter/<chapter_id>')
    def view_chapter(chapter_id):
        chapter = QZ_CHP_M.query.get_or_404(chapter_id)
        quizzes = QZ_QIZ_HDR.query.filter_by(QZ_QIZ_CHAP_ID=chapter_id).all()
        return render_template('view_chapter.html',chapter=chapter,quizzes=quizzes)
    
    # route to add quiz
    @app.route('/chapter/<chapter_id>/add_quiz',methods=['GET','POST'])
    def add_quiz(chapter_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        
        if request.method=='POST':
            quiz_name=request.form['quiz_name']
            quiz_desc = request.form['quiz_description']
            quiz_max= request.form['quiz_max']
            quiz_id = str(uuid.uuid4())[:10]
            subject_id=QZ_CHP_M.query.get(chapter_id).QZ_CHP_SUB_ID
            new_quiz = QZ_QIZ_HDR(
                QZ_QIZ_QUIZ_ID=quiz_id, 
                QZ_QIZ_QUIZ_NAME=quiz_name, 
                QZ_QIZ_DESC=quiz_desc, 
                QZ_QIZ_MAX=int(quiz_max), 
                QZ_QIZ_CHAP_ID=chapter_id,
                QZ_QIZ_SUB_ID=subject_id
            )

            db.session.add(new_quiz)
            db.session.commit()

            return redirect(url_for('view_chapter',chapter_id=chapter_id))
        return render_template('add_quiz.html',chapter_id=chapter_id)
    
    # route to add a new question
    @app.route('/quiz/<quiz_id>/add_question',methods=['POST','GET'])
    def add_question(quiz_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        if request.method=='POST':
            question_text= request.form['question_text']
            option_1= request.form['option_1']
            option_2 = request.form['option_2']
            option_3 = request.form['option_3']
            option_4 = request.form['option_4']
            correct_option = request.form['correct_option']

            question_id = str(uuid.uuid4())[:10]
            new_question = QZ_QTN_DET(
                QZ_QTN_ID=question_id,
                QZ_QTN_QUZ_ID=quiz_id,
                QZ_QTN_QUZ_DET=question_text,
                QZ_QTN_QTN_OPT_1=option_1,
                QZ_QTN_QTN_OPT_2=option_2,
                QZ_QTN_QTN_OPT_3=option_3,
                QZ_QTN_QTN_OPT_4=option_4,
                QZ_QTN_QTN_COR_OP=correct_option
            )

            db.session.add(new_question)
            db.session.commit()
            chapter_id=QZ_QIZ_HDR.query.filter_by(QZ_QIZ_QUIZ_ID=quiz_id).first().QZ_QIZ_CHAP_ID
            return redirect(url_for('view_chapter',chapter_id=chapter_id))
        return render_template('add_question.html',quiz_id=quiz_id)
    

    #route to take the quiz
    @app.route('/quiz/<quiz_id>/take',methods=['GET','POST'])
    def take_quiz(quiz_id):
        if 'username' not in session:
            return redirect(url_for('login'))
        quiz=QZ_QIZ_HDR.query.get_or_404(quiz_id)
        questions = QZ_QTN_DET.query.filter_by(QZ_QTN_QUZ_ID=quiz_id).all()
        if request.method=='POST':
            user_id=session['user_id']
            correct_count=0
            incorrect_count=0
            total_score=len(questions)
            for question in questions:
                user_answer=request.form.get(f'question_{question.QZ_QTN_ID}')
                if user_answer and user_answer.strip().lower() == question.QZ_QTN_QTN_COR_OP:
                    correct_count+=1
                else:
                    incorrect_count+=1

            attempt_id=store(user_id,quiz_id,correct_count,incorrect_count)
            return redirect(url_for('quiz_result',attempt_id=attempt_id))
        return render_template('take_quiz.html',quiz=quiz,questions=questions)
    
    def store(user_id,quiz_id,correct_count,incorrect_count):
        attempt_id = str(uuid.uuid4())[:10]
        attempt_time = datetime.now()

        new_attempt = QZ_ATM_HDR(
            QZ_ATM_ATMT_ID=attempt_id,
            QZ_ATM_QUIZ_ID=quiz_id,
            QZ_ATM_USER_ID=user_id,
            QZ_ATM_TIME=attempt_time.time(),
            QZ_ATM_SCORE=correct_count,
            QZ_ATM_DATE=attempt_time,
            QZ_ATM_CO=correct_count,
            QZ_ATM_INCO=incorrect_count
        )

        db.session.add(new_attempt)
        db.session.commit()

        return attempt_id
    

    # quiz result
    @app.route('/quiz_result/<attempt_id>')
    def quiz_result(attempt_id):
        if 'username' not in session:
            return redirect(url_for('login'))

        attempt = QZ_ATM_HDR.query.get_or_404(attempt_id)
        return render_template('quiz_result.html', attempt=attempt)

    # manage pre existing quiz
    @app.route('/quiz/<quiz_id>/manage', methods=['GET'])
    def view_quiz(quiz_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))

        quiz = QZ_QIZ_HDR.query.get_or_404(quiz_id)
        questions = QZ_QTN_DET.query.filter_by(QZ_QTN_QUZ_ID=quiz_id).all()

        return render_template('view_quiz.html', quiz=quiz, questions=questions)

    #update question
    @app.route('/quiz/<quiz_id>/update_question/<question_id>', methods=['GET', 'POST'])
    def update_question(quiz_id, question_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        question = QZ_QTN_DET.query.get_or_404(question_id)
        if request.method == 'POST':
            question.QZ_QTN_QUZ_DET = request.form['question_text']
            question.QZ_QTN_QTN_OPT_1 = request.form['option_1']
            question.QZ_QTN_QTN_OPT_2 = request.form['option_2']
            question.QZ_QTN_QTN_OPT_3 = request.form['option_3']
            question.QZ_QTN_QTN_OPT_4 = request.form['option_4']
            question.QZ_QTN_QTN_COR_OP = request.form['correct_option']
            db.session.commit()
            flash("Question updated successfully!", "success")
            return redirect(url_for('view_quiz', quiz_id=quiz_id))
        return render_template('update_question.html', quiz_id=quiz_id, question=question)
    
    #delete subject
    @app.route('/delete_subject/<subject_id>', methods=['POST'])
    def delete_subject(subject_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        subject = QZ_SUB_M.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return redirect(url_for('dashboard'))

    #delete chapter
    @app.route('/delete_chapter/<chapter_id>', methods=['POST'])
    def delete_chapter(chapter_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        chapter = QZ_CHP_M.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        return redirect(url_for('view_subject', subject_id=chapter.QZ_CHP_SUB_ID))
    #delete quiz
    @app.route('/delete_quiz/<quiz_id>', methods=['POST'])
    def delete_quiz(quiz_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        quiz = QZ_QIZ_HDR.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        return redirect(url_for('view_chapter', chapter_id=quiz.QZ_QIZ_CHAP_ID))
    
    # delete question
    @app.route('/delete_question/<question_id>', methods=['POST'])
    def delete_question(question_id):
        if 'username' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))

        question = QZ_QTN_DET.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return redirect(url_for('view_quiz', quiz_id=question.QZ_QTN_QUZ_ID))
    
    #seach functionality
    @app.route('/search', methods=['GET'])
    def search():
        if 'username' not in session:
            return redirect(url_for('login'))

        query = request.args.get('query', '').strip()

        if not query:
            return render_template('search_results.html', results=[], query=query)

        # Search subjects, chapters, and quizzes
        subjects = QZ_SUB_M.query.filter(QZ_SUB_M.QZ_SUB_NAME.ilike(f"%{query}%")).all()
        chapters = QZ_CHP_M.query.filter(QZ_CHP_M.QZ_CHP_NAME.ilike(f"%{query}%")).all()
        quizzes = QZ_QIZ_HDR.query.filter(QZ_QIZ_HDR.QZ_QIZ_QUIZ_NAME.ilike(f"%{query}%")).all()

        results = {
            "subjects": subjects,
            "chapters": chapters,
            "quizzes": quizzes
        }

        return render_template('search_results.html', results=results, query=query,role=session['username'])
    

    def generate_report(user_id, is_admin):
            

            if is_admin:
                subjects = db.session.query(QZ_SUB_M).all()
                chapters_count = {sub.QZ_SUB_NAME: len(sub.chapters) for sub in subjects}

                quizzes_per_chapter = (
                    db.session.query(QZ_CHP_M.QZ_CHP_NAME, db.func.count(QZ_QIZ_HDR.QZ_QIZ_QUIZ_ID))
                    .join(QZ_QIZ_HDR, QZ_CHP_M.QZ_CHP_CHAP_ID == QZ_QIZ_HDR.QZ_QIZ_CHAP_ID)
                    .group_by(QZ_CHP_M.QZ_CHP_NAME)
                    .all()
                )

                subject_scores = (
                    db.session.query(QZ_SUB_M.QZ_SUB_NAME, db.func.sum(QZ_ATM_HDR.QZ_ATM_SCORE), db.func.sum(QZ_QIZ_HDR.QZ_QIZ_MAX))
                    .join(QZ_QIZ_HDR, QZ_SUB_M.QZ_SUB_ID == QZ_QIZ_HDR.QZ_QIZ_SUB_ID)
                    .join(QZ_ATM_HDR, QZ_QIZ_HDR.QZ_QIZ_QUIZ_ID == QZ_ATM_HDR.QZ_ATM_QUIZ_ID)
                    .group_by(QZ_SUB_M.QZ_SUB_NAME)
                    .all()
                )
                subjects_list = list(chapters_count.keys())
                chapters_list = list(chapters_count.values())

                chapters_names = [chap[0] for chap in quizzes_per_chapter]
                quizzes_counts = [chap[1] for chap in quizzes_per_chapter]

                subject_names = [sub[0] for sub in subject_scores]
                scores = [sub[1] for sub in subject_scores]
                max_scores = [sub[2] for sub in subject_scores]

                #admin graphs
                def create_bar_chart(labels, values, title, xlabel, ylabel, color):
                    fig, ax = plt.subplots(figsize=(8, 5))
                    x = range(len(labels))
                    ax.bar(x, values, color=color)
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels, rotation=45, ha="right")
                    ax.set_title(title)
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)

                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)
                    encoded_chart = base64.b64encode(buf.getvalue()).decode("utf-8")
                    plt.close()

                    return encoded_chart

                bar_chart_1 = create_bar_chart(subjects_list, chapters_list, "Number of Chapters per Subject", "Subjects", "Chapters", "blue")
                bar_chart_2 = create_bar_chart(chapters_names, quizzes_counts, "Number of Quizzes per Chapter", "Chapters", "Quizzes", "green")
                pie_chart = create_bar_chart(subject_names, scores, "Score Distribution per Subject", "Subjects", "Total Marks", "red")

                return bar_chart_1, bar_chart_2, pie_chart

            else:
                subject_scores = (
                    db.session.query(QZ_SUB_M.QZ_SUB_NAME, db.func.sum(QZ_ATM_HDR.QZ_ATM_SCORE), db.func.sum(QZ_QIZ_HDR.QZ_QIZ_MAX))
                    .join(QZ_QIZ_HDR, QZ_SUB_M.QZ_SUB_ID == QZ_QIZ_HDR.QZ_QIZ_SUB_ID)
                    .join(QZ_ATM_HDR, QZ_QIZ_HDR.QZ_QIZ_QUIZ_ID == QZ_ATM_HDR.QZ_ATM_QUIZ_ID)
                    .filter(QZ_ATM_HDR.QZ_ATM_USER_ID == user_id)
                    .group_by(QZ_SUB_M.QZ_SUB_NAME)
                    .all()
                )

                chapter_scores = (
                    db.session.query(QZ_CHP_M.QZ_CHP_NAME, db.func.sum(QZ_ATM_HDR.QZ_ATM_SCORE), db.func.sum(QZ_QIZ_HDR.QZ_QIZ_MAX))
                    .join(QZ_QIZ_HDR, QZ_CHP_M.QZ_CHP_CHAP_ID == QZ_QIZ_HDR.QZ_QIZ_CHAP_ID)
                    .join(QZ_ATM_HDR, QZ_QIZ_HDR.QZ_QIZ_QUIZ_ID == QZ_ATM_HDR.QZ_ATM_QUIZ_ID)
                    .filter(QZ_ATM_HDR.QZ_ATM_USER_ID == user_id)
                    .group_by(QZ_CHP_M.QZ_CHP_NAME)
                    .all()
                )

                latest_attempts_subquery = (
                                            db.session.query(
                                                QZ_ATM_HDR.QZ_ATM_QUIZ_ID,
                                                func.max(QZ_ATM_HDR.QZ_ATM_DATE).label("latest_date")
                                            )
                                            .filter(QZ_ATM_HDR.QZ_ATM_USER_ID == user_id)
                                            .group_by(QZ_ATM_HDR.QZ_ATM_QUIZ_ID)
                                            .subquery()
                                        )

                # Main query to get quiz names and latest scores
                quiz_scores = (
                    db.session.query(
                        QZ_QIZ_HDR.QZ_QIZ_QUIZ_NAME,
                        QZ_ATM_HDR.QZ_ATM_SCORE,
                        QZ_QIZ_HDR.QZ_QIZ_MAX
                    )
                    .join(QZ_ATM_HDR, QZ_QIZ_HDR.QZ_QIZ_QUIZ_ID == QZ_ATM_HDR.QZ_ATM_QUIZ_ID)
                    .join(latest_attempts_subquery, 
                        (QZ_ATM_HDR.QZ_ATM_QUIZ_ID == latest_attempts_subquery.c.QZ_ATM_QUIZ_ID) &
                        (QZ_ATM_HDR.QZ_ATM_DATE == latest_attempts_subquery.c.latest_date))
                    .filter(QZ_ATM_HDR.QZ_ATM_USER_ID == user_id)
                    .order_by(desc(QZ_ATM_HDR.QZ_ATM_DATE))
                    .all()
                )

                
                subject_names = [sub[0] for sub in subject_scores]
                subject_scores_obtained = [sub[1] for sub in subject_scores]
                subject_scores_max = [sub[2] for sub in subject_scores]

                chapter_names = [chap[0] for chap in chapter_scores]
                chapter_scores_obtained = [chap[1] for chap in chapter_scores]
                chapter_scores_max = [chap[2] for chap in chapter_scores]

                if quiz_scores:
                    quiz_names = [quiz[0] for quiz in quiz_scores]
                    quiz_scores_obtained = [quiz[1] for quiz in quiz_scores]
                    quiz_scores_max = [quiz[2] for quiz in quiz_scores]
                else:
                    quiz_names = []
                    quiz_scores_obtained = []
                    quiz_scores_max = []

                #student  grpahs
                def create_student_chart(labels, values, max_values, title):
                    fig, ax = plt.subplots(figsize=(8, 5))
                    x = range(len(labels))
                    ax.bar(x, max_values, color='lightgray', label="Max Marks")
                    ax.bar(x, values, color='blue', label="Your Marks")
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels, rotation=45, ha="right")
                    ax.set_title(title)
                    ax.legend()

                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)
                    encoded_chart = base64.b64encode(buf.getvalue()).decode("utf-8")
                    plt.close()

                    return encoded_chart

                subject_chart = create_student_chart(subject_names, subject_scores_obtained, subject_scores_max, "Marks per Subject")
                chapter_chart = create_student_chart(chapter_names, chapter_scores_obtained, chapter_scores_max, "Marks per Chapter")
                quiz_chart = create_student_chart(quiz_names, quiz_scores_obtained, quiz_scores_max, "Marks per Quiz")

                return subject_chart, chapter_chart, quiz_chart


    @app.route('/report')
    def report():
        """Dynamically render report for both Admins and Students."""
        user_id = session.get("user_id")
        is_admin = session['role'] == "admin"

        if not user_id:
            return redirect(url_for("login"))

        charts = generate_report(user_id, is_admin)

        return render_template("report.html", is_admin=is_admin, charts=charts)