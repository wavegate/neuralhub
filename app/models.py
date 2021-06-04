from datetime import datetime
import datetime as dt
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from app import db, login

##### USERS ######

class User(UserMixin, db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	admin = db.Column(db.Boolean())
	tests = db.relationship('Test', backref='author', lazy='dynamic')
	tasks = db.relationship('Task', backref='author', lazy='dynamic')
	mice = db.relationship('Mouse', backref='owner', lazy='dynamic')
	cages = db.relationship('Cage', backref='owner', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			current_app.config['SECRET_KEY'],
			algorithm='HS256')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

##### BLOG #####

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

##### COGNITION #####

class Test(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	testname = db.Column(db.String(140))
	score = db.Column(db.String(140))
	accuracy = db.Column(db.String(140))
	reaction_time = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	language = db.Column(db.String(5))

	def __repr__(self):
		return '<Test {}: {}>'.format(self.testname, self.score)

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	taskname = db.Column(db.String(500))
	date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	notes = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


###### MICE #####

class Mouse(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sex = db.Column(db.String(500))
	genotype = db.Column(db.String(500))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	dob = db.Column(db.DateTime)
	cage = db.Column(db.Integer, db.ForeignKey('cage.id'))
	cagetag = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	notes = db.Column(db.Text)

	def age(self):
		return (datetime.now() - self.dob).days

class Cage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tag = db.Column(db.String(500))
	mice = db.relationship('Mouse', backref='house', lazy='dynamic')
	notes = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	mouseline = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))