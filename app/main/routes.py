from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
	jsonify, current_app, Response, stream_with_context, make_response, session, send_file, send_from_directory, safe_join, abort, Response
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, csrf, socketio
from app.main.forms import EmptyForm, PostForm, SLUMSForm
from app.models import User, Post, Test, Task
from app.translate import translate
from app.main import bp
from app.auth.email import send_feedback_email
from app.nocache import nocache
import logging
import re
import flask_excel as excel
import pandas as pd
import datetime as dt
import dateutil.parser
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
import base64
import json
import glob
import dateparser
import math
import time
import ast
from flask_socketio import join_room, leave_room, emit
from molmass import Formula

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	return render_template('base.html')

@bp.route('/postmethod', methods = ['POST'])
@csrf.exempt
def get_post_javascript_data():
	test_name = request.form['test_name']
	accuracy = request.form['accuracy']
	score = accuracy
	rt = request.form['rt']
	#print(jsdata, file=sys.stderr)
	#with open('somefile.txt', 'a') as the_file:
	#    the_file.write(jsdata)
	files = glob.glob('app/static/img/subitizing/*') #remove subitizing images, must change once more tests added
	for f in files:
		os.remove(f)
	test = Test(testname=test_name, score=score, reaction_time=rt, accuracy=accuracy, author=current_user)
	db.session.add(test)
	db.session.commit()
	return rt

@bp.route("/cognition", methods = ['GET'])
@login_required
def cognition():
	tests = current_user.tests.order_by(Test.timestamp.desc()).all()
	return render_template('cognition.html', tests=tests)

@bp.route("/test1", methods = ['GET'])
@login_required
def test1():
	return render_template('test1.html')

@bp.route("/posts", methods = ['GET'])
@login_required
def posts():
	if current_user.admin:
		return render_template('posts.html', posts=Post.query.all())
	else:
		return redirect(request.referrer or url_for('main.index'))

@bp.route("/post/<int:id>", methods = ['GET'])
@login_required
def post(id):
	post = Post.query.get(id)
	return render_template('post.html', post=post)

@bp.route("/task/<int:id>", methods = ['GET'])
@login_required
def task(id):
	task = Task.query.get(id)
	return render_template('task.html', task=task)

@bp.route("/create_post", methods = ['GET', 'POST'])
@login_required
@csrf.exempt
def create_post():
	if request.method == 'POST':
		post = Post(body=request.form.get('editordata'), author=current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('main.post', id=post.id))
	return render_template('create_post.html')

@bp.route("/create_task", methods = ['GET', 'POST'])
@login_required
@csrf.exempt
def create_task():
	if request.method == 'POST':
		date_in = request.form.get('time')
		date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
		date_processing = [int(v) for v in date_processing]
		date_out = dt.datetime(*date_processing)
		task = Task(date=date_out, taskname=request.form.get('taskname'), notes=request.form.get('editordata'), author=current_user)
		db.session.add(task)
		db.session.commit()
		return redirect(url_for('main.task', id=task.id))
	return render_template('create_task.html')

@bp.route("/delete_post/<int:id>", methods = ['GET', 'POST'])
@login_required
def delete_post(id):
	post = Post.query.get(id)
	db.session.delete(post)
	db.session.commit()
	return redirect(url_for('main.post', id=post.id))

@bp.route("/delete_task/<int:id>", methods = ['GET', 'POST'])
@login_required
def delete_task(id):
	task = Task.query.get(id)
	db.session.delete(task)
	db.session.commit()
	return redirect(url_for('main.tasks'))

@bp.route("/edit_post/<int:id>", methods = ['GET', 'POST'])
@login_required
@csrf.exempt
def edit_post(id):
	post = Post.query.get(id)
	if request.method == 'POST':
		post.body = request.form.get('editordata')
		db.session.commit()
		return redirect(url_for('main.post', id=post.id))
	return render_template('edit_post.html', post=post)

@bp.route("/edit_task/<int:id>", methods = ['GET', 'task'])
@login_required
@csrf.exempt
def edit_task(id):
	task = task.query.get(id)
	if request.method == 'POST':
		date_in = request.form.get('time')
		date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
		date_processing = [int(v) for v in date_processing]
		date_out = dt.datetime(*date_processing)
		task.taskname = request.form.get('taskname')
		task.date = date_out
		task.notes = request.form.get('editordata')
		db.session.commit()
		return redirect(url_for('main.task', id=task.id))
	return render_template('edit_task.html', task=task)

@bp.route("/save_post/<int:id>", methods = ['GET'])
@nocache
@login_required
def save_post(id):
	post = Post.query.get(id)
	file = open("post.txt", "w")
	file.write(post.body)
	file.close()
	return send_file("post.txt", as_attachment=True)

@bp.route("/trpc5", methods = ['GET'])
@login_required
def trpc5():
	return render_template('trpc5.html')

@bp.route("/introtoelectronics", methods = ['GET'])
@login_required
def introtoelectronics():
	return render_template('introtoelectronics.html')

@bp.route("/tasks", methods = ['GET'])
@login_required
def tasks():
	return render_template('tasks.html', tasks=Task.query.filter_by(user_id=current_user.id))

@bp.route("/electricalengineering", methods = ['GET'])
@login_required
def electricalengineering():
	return render_template('electricalengineering.html')

@bp.route("/aCSF", methods = ['GET'])
@login_required
def aCSF():
	toCheck = {'NaCl': 124,'KCl': 5,'C8H18N2O4S': 20,'C6H12O6': 10,'MgCl2': 1.3,'CaCl2.2H2O': 1.5,'NaHCO3': 26,'NaH2PO4.2H2O': 1.25}
	volume = 0.4
	end = []
	for key, value in toCheck.items():
		form = Formula(key)
		tup = (form, '%s' % float('%.3g' % (volume * form.mass * value * 0.001)))
		end.append(tup)
	result = dict(end)
	return render_template('aCSF.html', result=result, volume = volume)

@bp.route("/machinelearning", methods = ['GET'])
@login_required
def machinelearning():
	return render_template('machinelearning.html')

@bp.route("/subitizing", methods = ['GET'])
@login_required
def subitizing():
	return render_template('subitizing.html')

@bp.route("/jack", methods = ['GET'])
@login_required
def jack():
	return render_template('jackofalltrades.html')

@bp.route("/ultrasound", methods = ['GET'])
@login_required
def ultrasound():
	return render_template('ultrasound.html')

@bp.route("/nback", methods = ['GET'])
@login_required
def nback():
	return render_template('nback.html')

@bp.route("/phone", methods = ['GET'])
@login_required
def phone():
	return render_template('phone.html')

@bp.route("/painmodulation", methods = ['GET'])
@login_required
def painmodulation():
	return render_template('painmodulation.html')

@bp.route("/moocs", methods = ['GET'])
@login_required
def moocs():
	return render_template('moocs.html')

@bp.route("/companies", methods = ['GET'])
@login_required
def companies():
	return render_template('companies.html')

@bp.route("/ethics", methods = ['GET'])
@login_required
def ethics():
	return render_template('ethics.html')

@bp.route("/penfield", methods = ['GET'])
@login_required
def penfield():
	return render_template('penfield.html')

@bp.route("/programminglanguages", methods = ['GET'])
@login_required
def programminglanguages():
	return render_template('programminglanguages.html')

@bp.route("/edu", methods = ['GET'])
@login_required
def edu():
	return render_template('edu.html')

@bp.route("/drg", methods = ['GET'])
@login_required
def drg():
	if current_user.admin:
		return render_template('drg.html')
	else: 
		return redirect(url_for('main.index'))

@bp.route("/bmi", methods = ['GET'])
def bmi():
	return render_template('bmi.html')

@bp.route("/bmiserruya", methods = ['GET'])
def bmiserruya():
	return render_template('bmiserruya.html')

@bp.route("/unity", methods = ['GET'])
@login_required
def unity():
	return render_template('unity.html')

@bp.route("/det", methods = ['GET'])
def det():
	return render_template('det.html')

@bp.route("/slums", methods = ['GET', 'POST'])
@login_required
def slums():
	form = SLUMSForm()
	if form.validate_on_submit():
		return render_template('slums.html', form=form)
	return render_template('slums.html', form=form)

@bp.route('/delete_test/<int:test_id>')
@login_required
def delete_test(test_id):
	test = Test.query.get(test_id)
	if test.author == current_user:
		db.session.delete(test)
		db.session.commit()
	return redirect(request.referrer or url_for('cognition'))

@bp.route('/generate_images')
def generate_images():
	sequence = []
	for i in range(5):
		N = np.random.random_integers(1,9)
		x = np.random.rand(N)
		y = np.random.rand(N)
		new_dict = {}
		new_dict['index'] = str(N)

		colors = 'k'
		area = 20

		plt.scatter(x, y, s=area, c=colors)
		plt.axis([0, 1, 0, 1])
		plt.axis('scaled')

		plt.axis('off')
		loc = 'img/subitizing/{}.png'.format(np.random.random_integers(10000000,90000000))
		loc2 = 'app/static/' + loc
		new_dict['loc'] = loc
		if os.path.isfile(loc2):
			os.remove(loc2)

		plt.savefig(loc2)
		sequence.append(new_dict)
		plt.clf()
	return json.dumps(sequence)


@bp.route('/about', methods=['GET','POST'])
def about():
	form = FeedbackForm()
	if form.validate_on_submit():
		send_feedback_email(form)
		flash(_('Feedback submitted!'))
		return redirect(url_for('main.about'))
	return render_template('about.html', form=form)

@bp.route('/settings')
def settings():
	specialty2 = session.get('specialty')
	return render_template('settings.html', specialty2=specialty2)