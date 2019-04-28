from camera import VideoCamera
#from word_training import models
from flask import render_template, request, jsonify, Response, flash, url_for, redirect
from irecruit.forms import AdminloginForm, AdminForm, LoginForm, DetailsForm, AddQuestionForm
from irecruit.models import Question, Admin, User, Skill
from irecruit import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required, user_logged_in
from sqlalchemy import update
import random
import requests
import nltk
import cv2
from pyemd import emd
from nltk.corpus import stopwords
from bs4 import BeautifulSoup, NavigableString, Tag
import urllib.parse as urlparse
from flask_mail import Message
from detect import VideoCameraDetection
#from nltk import download
#download('stopwords')
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
flag = 0



@app.route('/chat_retrieval')
def chat_retrieval():

        global correct_answer
        global next_question
        global scores
        counts = request.args.get('count')
        adm_id = Admin.query.get(current_user.id)
        scores = adm_id.score
        id = Skill.query.get(current_user.id)
        skills = {}
        for column in id.__table__.columns:
            skills[column.name] = str(getattr(id, column.name))
        skill_lang = []
        skill_lang.extend((skills['level1'] + ":" + skills['skill1'], skills['level2'] + ":" + skills['skill2'],
                           skills['level3'] + ":" + skills['skill3'], skills['level4'] + ":" + skills['skill4']))
        print(skills)
        print(skill_lang)
        while True:
            i = random.randint(0, len(skill_lang) - 1)
            lang = skill_lang[i]
            user_level, user_language = lang.split(":")
            if not user_language:
                continue
            else:
                break
        print(user_level)
        print(user_language)
        items = Question.query.filter(Question.question_language.like(user_language)).\
            filter(Question.question_level.like(user_level)).all()
        if counts == '0':
            while True:
                i = random.randint(0, len(items) - 1)
                if items[i].question_chosen == 0:
                    break
            next_question = items[i]
            correct_answer = next_question.question_answer
            next_question.question_chosen = 0
            db.session.commit()
            results = [next_question.question, 1]
            return jsonify(result=results)
        else:
            answr = request.args.get('answer')
            print(correct_answer)
            print(answr)
            distance = similarity(answr, correct_answer, scores)
            if distance < 3:
                while True:
                    i = random.randint(0, len(items) - 1)
                    if items[i].question_chosen == 0:
                        break
                next_question = items[i]
                correct_answer = next_question.question_answer
                next_question.question_chosen = 0
                db.session.commit()
                results = [next_question.question, 1]
                return jsonify(result=results)
            else:
                nouns = []
                for word, pos in nltk.pos_tag(nltk.word_tokenize(str(answr))):
                        if pos.startswith('NN'):
                            nouns.append(word)
                print(nouns)
                i = random.randint(0, len(nouns) - 1)
                words = nouns[i]
                language = next_question.question_language
                next_question1 = "What do you mean by " + words
                answer = words + " in " + language
                correct_answer = scrape_answer(answer, language)
                results = [next_question1, 1]
                return jsonify(result=results)


def similarity(given_answer, db_answer, marks):
    given_answer = given_answer.lower().split()
    db_answer = db_answer.lower().split()
    stop_words = stopwords.words('english')
    given_answer = [w for w in given_answer if w not in stop_words]
    db_answer = [w for w in db_answer if w not in stop_words]
    distance = models.wmdistance(given_answer, db_answer)
    if distance == 0.0:
        marks = marks + 10
    elif 0 < distance <= 1:
        marks = marks + 8
    elif 1 < distance <= 2:
        marks = marks + 7
    elif 2 < distance <= 3:
        marks = marks + 5
    elif 3 < distance <= 4:
        marks = marks + 3
    else:
        marks = marks + 0
    id = Admin.query.get(current_user.id)
    query = update(Admin).where(id.email == Admin.email).values(score=marks)
    db.session.execute(query)
    print(distance)
    return distance


def scrape_answer(ans, lang):
    global stri
    url = 'http://www.google.com/search?q=' + ans
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all("a")
    if lang == "java" or lang == "cpp":
        for link in links:
            if "www.javatpoint.com" in str(link):
                stri = str(link.get('href'))
                break
    elif lang == "dbms" or lang == "c" or lang == "php" or lang == "python":
        for link in links:
            if "www.tutorialspoint.com" in str(link):
                print(link.get('href'))
                stri = str(link.get('href'))
                break
    data = stri.split("&")
    parsed = urlparse.urlparse(data[0])
    h = urlparse.parse_qs(parsed.query)['q']
    page1 = requests.get(h[0])
    soup1 = BeautifulSoup(page1.text, "html.parser")

    if lang == "java" or lang == "cpp":
        a = ""
        for header in soup1.find_all('h1'):
            nextNode = header
            while True:
                nextNode = nextNode.nextSibling
                if nextNode is None:
                    break
                if isinstance(nextNode, NavigableString):
                    (nextNode.strip())
                if isinstance(nextNode, Tag):
                    if nextNode.name == "h3":
                        break
                    a = a + nextNode.get_text(strip=True).strip()
        return a
    elif lang == "dbms" or lang == "c" or lang == "php" or lang == "python":
        for header in soup1.find_all('h1'):
            nextNode = header
            while True:
                nextNode = nextNode.nextSibling
                if nextNode is None:
                    break
                if isinstance(nextNode, NavigableString):
                    (nextNode.strip())
                if isinstance(nextNode, Tag):
                    if nextNode.name == "h2":
                        break
                    return nextNode.get_text(strip=True).strip()
    else:
        print("invalid")


@app.route('/face_detection')
def face_detection():
        return render_template('face_detection.html')


def gen(camera):
    count = 0
    while True:
        if count > 100:
            cv2.VideoCapture(0).release()
            break
        else:
            frame, count1 = camera.get_frame(count)
            print(count1)
            count = count1
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/detect')
def detect():
    return Response(gen(VideoCameraDetection()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/chat_interview')
def chat_interview():
    if current_user.is_authenticated:
        return render_template('chat.html', items=Question.query.all())
    else:
        flash('You are not logged in! Please login', 'danger')
        return redirect(url_for('home'))


def gen1(camera):
    global cnt
    while True:
        frame, cnt = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen1(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/", methods = ['POST', 'GET'])
@app.route("/home", methods = ['POST', 'GET'])
def home():
    db.create_all()
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You can enter your details now!', 'success')
            return redirect(url_for('details'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return redirect(url_for('home'))
    return render_template('login1.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('exit.html')


@app.route("/details", methods=['POST', 'GET'])
def details():

    if current_user.is_authenticated:
        form = DetailsForm()
        if form.validate_on_submit():
            print("hi")
            try:
                user = User(firstname=form.firstname.data, lastname=form.lastname.data, dob=form.dob.data, user_id = current_user.id)
                skills = Skill(skill1=form.skill1.data, level1=form.level1.data,
                                skill2=form.skill2.data, level2=form.level2.data,
                                skill3=form.skill3.data, level3=form.level3.data,
                                skill4=form.skill4.data, level4=form.level4.data, user_id = current_user.id)
                db.session.add(user)
                db.session.add(skills)
                db.session.commit()
                flash('Your details has been submitted! You are now able to take the test', 'success')
                return redirect(url_for('detection'))
            except:
                db.session.rollback()
                flash('Your details already exist! You can\'t retake test', 'danger')
                return redirect(url_for('logout'))
    else:
        flash('You are not logged in! Please login', 'danger')
        return redirect(url_for('home'))
    return render_template('details.html', title='Details', form=form)


@app.route('/detection')
def detection():
    return render_template('detection.html')


@app.route('/view_users')
def view_users():
    db.create_all()
    users = Admin.query.all()
    usr = User.query.all()
    return render_template('view_users.html', users=users, usr=usr)


@app.route('/add_questions', methods = ['POST', 'GET'])
def add_questions():
    if flag:
        form = AddQuestionForm()
        if form.validate_on_submit():
            try:
                question = Question(question_id=form.Id.data, question=form.Question.data, question_answer=form.Answer.data,
                                question_level=form.Level.data, question_language=form.Language.data)
                db.session.add(question)
                db.session.commit()
                flash('Question Added Successfully', 'success')
                return redirect(url_for('add_questions'))
            except:
                db.session.rollback()
                flash('Something Went Wrong', 'danger')
                return redirect(url_for('add_questions'))
    else:
        flash('Admin not logged in!', 'danger')
        return redirect(url_for('adminlogin'))

    return render_template('add_questions.html', form=form)


@app.route("/adminlogin", methods = ['POST', 'GET'])
def adminlogin():
    form = AdminloginForm()
    if form.validate_on_submit():
        if form.username.data == "aravindcv" and form.password.data == "password":
            global flag
            flag = 1
            db.create_all()
            flash('Admin verified!', 'success')
            return redirect(url_for('admin'))
    return render_template('adminlogin.html', title='Admin-Login', form=form)


@app.route("/passe", methods=['POST', 'GET'])
def passe():
    receiver = request.form.get('send')
    print(receiver)
    rec = []
    rec.append(receiver)
    msg = Message('Sorry', sender='nadeemnazer123@gmail.com', recipients = rec)
    msg.body = "Sorry you have not passed! All the best for future." \
               "This is an electronic mail. Please dont respond to it."

    mail.send(msg)
    flash("Message sent", 'success')
    return redirect(url_for('view_users'))


@app.route("/passe_mails", methods=['POST', 'GET'])
def passe_mails():
    receiver = request.form.get('send')
    print(receiver)
    rec = []
    rec.append(receiver)
    msg = Message('Greetings', sender='nadeemnazer123@gmail.com', recipients=rec)
    msg.body = "Congratulaitons! You have cleared the test! We will contact you soon." \
               "This is an electronic mail. Please dont respond to it."

    mail.send(msg)
    flash("Message sent", 'success')
    return redirect(url_for('view_users'))


@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if flag:
        form = AdminForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Admin(email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('User added to the database successfully', 'success')
    else:
        flash('Admin not logged in!', 'danger')
        return redirect(url_for('adminlogin'))
    return render_template('admin.html', title='Admin', form=form)



