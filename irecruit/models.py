from irecruit import db, login_manager
from flask_login import UserMixin


class Question(db.Model):
    question_id = db.Column(db.VARCHAR(10), primary_key=True)
    question = db.Column(db.VARCHAR(500), unique=True)
    question_answer = db.Column(db.VARCHAR(500))
    question_level = db.Column(db.VARCHAR(20))
    question_language = db.Column(db.VARCHAR(20))
    question_chosen = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Question('{self.question}', {self.question_language}, {self.question_level})"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    user = db.relationship('User', backref='admin', uselist=False)
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.id}', '{self.email}', '{self.score}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admin.id'), unique=True)
    skill = db.relationship('Skill', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.firstname}', '{self.lastname}', '{self.user_id}')"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill1 = db.Column(db.String(20), nullable=False)
    level1 = db.Column(db.String(20), nullable=False, default='Beginner')
    skill2 = db.Column(db.String(20))
    level2 = db.Column(db.String(20), nullable=False, default='Beginner')
    skill3 = db.Column(db.String(20))
    level3 = db.Column(db.String(20), nullable=False, default='Beginner')
    skill4 = db.Column(db.String(20))
    level4 = db.Column(db.String(20), nullable=False, default='Beginner')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True)

    def __repr__(self):
        return (f"Skill('{self.skill1}:{self.level1}', '{self.skill2}:{self.level2}', '{self.skill3}:{self.level3}', "
                f"'{self.skill4}:{self.level4}')")


class Company(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(20), nullable=False)
   password = db.Column(db.String(60), nullable=False)

   def __repr__(self):
        return f"User('{self.id}', '{self.username}')"
