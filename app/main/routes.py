from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
	jsonify, current_app, Response, stream_with_context, make_response, session
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, csrf, socketio
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, MessageForm, ProgramForm, AddInterviewForm, FeedbackForm, SLUMSForm, CreateSpecialtyForm, SpecialtyForm, ThreadForm
from app.models import User, Post, Program, Message, Notification, Interview, Interview_Date, Test, Specialty, Thread, Interview_Impression, Chat
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

@bp.route("/subitizing", methods = ['GET'])
@login_required
def subitizing():
	return render_template('subitizing.html')

@bp.route("/nback", methods = ['GET'])
@login_required
def nback():
	return render_template('nback.html')

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
	return render_template('drg.html')

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

@bp.route('/delete_post/<int:post_id>', methods=['GET','POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get(post_id)
	if current_user == post.author:
		db.session.delete(post)
		db.session.commit()
		flash('Post deleted!')
	return redirect(request.referrer)

@bp.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
	specialty2 = session.get('specialty')
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.user', username=user.username,
					   page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.user', username=user.username,
					   page=posts.prev_num) if posts.has_prev else None
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit() and current_user == user:
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash(_('Your changes have been saved.'))
		return render_template('user.html', user=user, interviews=user.interviews,posts=posts.items,next_url=next_url,prev_url=prev_url,form=form)
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('user.html', specialty2=specialty2, user=user, interviews=user.interviews,posts=posts.items, programs=user.programs,
						   next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
	specialty2 = session.get('specialty')
	user = User.query.filter_by(username=recipient).first_or_404()
	form = MessageForm()
	if form.validate_on_submit():
		msg = Message(author=current_user, recipient=user,
					  body=form.message.data)
		db.session.add(msg)
		user.add_notification('unread_message_count', user.new_messages())
		db.session.commit()
		flash(_('Your message has been sent.'))
		return redirect(url_for('main.user', username=recipient))
	return render_template('send_message.html', specialty2=specialty2, title=_('Send Message'),
						   form=form, recipient=recipient)

@bp.route('/messages')
@login_required
def messages():
	specialty2 = session.get('specialty')
	current_user.last_message_read_time = datetime.utcnow()
	current_user.add_notification('unread_message_count', 0)
	db.session.commit()
	page = request.args.get('page', 1, type=int)
	messages = current_user.messages_received.order_by(
		Message.timestamp.desc()).paginate(
			page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.messages', page=messages.next_num) \
		if messages.has_next else None
	prev_url = url_for('main.messages', page=messages.prev_num) \
		if messages.has_prev else None
	return render_template('messages.html', specialty2=specialty2, messages=messages.items,
						   next_url=next_url, prev_url=prev_url)

@bp.route('/notifications')
@login_required
def notifications():
	since = request.args.get('since', 0.0, type=float)
	notifications = current_user.notifications.filter(
		Notification.timestamp > since).order_by(Notification.timestamp.asc())
	return jsonify([{
		'name': n.name,
		'data': n.get_data(),
		'timestamp': n.timestamp
	} for n in notifications])


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


@bp.route('/chat/<int:id>', methods=['GET', 'POST'])
@csrf.exempt
def chat(id):
	specialty2 = session.get('specialty')
	specialty = Specialty.query.get(id)
	session['room'] = str(specialty.id)
	chats = Chat.query.filter_by(specialty=specialty).order_by(Chat.timestamp.asc())[0:25]
	if current_user.is_authenticated:
		name = current_user.username
	else:
		name = 'anonymous'
	room = specialty.name
	if name == '' or room == '':
		return redirect(request.referrer)
	return render_template('chat.html', name=name, room=room, specialty=specialty, specialty2=specialty2, chats=chats)

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    specialty=Specialty.query.get(room)
    #if current_user.is_authenticated:
    #	emit('status', {'msg': current_user.username + ' has entered the room.'}, room=room)
    #	chat = Chat(author=current_user, text=current_user.username + ' has entered the room.', specialty=specialty)
    #else:
    #	emit('status', {'msg': 'anonymous has entered the room.'}, room=room)
    #	chat = Chat(text='anonymous has entered the room.', specialty=specialty)
    #db.session.add(chat)
    #if Chat.query.count() > 25:
    #	oldest_chat = Chat.query.order_by(Chat.timestamp.asc())[0]
    #	db.session.delete(oldest_chat)
    #db.session.commit()

@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    specialty=Specialty.query.get(room)
    if current_user.is_authenticated:
    	emit('message', {'msg': current_user.username + ': ' + message['msg']}, room=room)
    	chat = Chat(author=current_user, text=current_user.username + ': ' + message['msg'], specialty=specialty)
    else:
    	emit('message', {'msg': 'anonymous'+ ': ' + message['msg']}, room=room)
    	chat = Chat(text='anonymous'+ ': ' + message['msg'], specialty=specialty)
    db.session.add(chat)
    if Chat.query.count() > 25:
    	oldest_chat = Chat.query.order_by(Chat.timestamp.asc())[0]
    	db.session.delete(oldest_chat)
    db.session.commit()

@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    specialty=Specialty.query.get(room)
    if current_user.is_authenticated:
    	emit('status', {'msg': current_user.username + ' has left the room.'}, room=room)
    	chat = Chat(author=current_user, text=current_user.username + ' has left the room.', specialty=specialty)
    else:
    	emit('status', {'msg': 'anonymous has left the room.'}, room=room)
    	chat = Chat(text='anonymous has left the room.', specialty=specialty)
    db.session.add(chat)
    if Chat.query.count() > 25:
    	oldest_chat = Chat.query.order_by(Chat.timestamp.asc())[0]
    	db.session.delete(oldest_chat)
    db.session.commit()

@bp.route('/forum/<int:specialty_id>', methods=['GET', 'POST'])
def threads(specialty_id):
	specialty2 = session.get('specialty')
	page = request.args.get('page', 1, type=int)
	specialty = Specialty.query.get(specialty_id)
	threads = specialty.threads.order_by(Thread.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.specialty', specialty_id=specialty_id,
					   page=threads.next_num) if threads.has_next else None
	prev_url = url_for('main.specialty', specialty_id=specialty_id,
					   page=threads.prev_num) if threads.has_prev else None
	return render_template('threads.html', specialty2 = specialty2, next_url=next_url, prev_url=prev_url, specialty=specialty, threads=threads.items)

@bp.route('/new_thread/<int:specialty_id>', methods=['GET', 'POST'])
def new_thread(specialty_id):
	specialty2 = session.get('specialty')
	threadform = ThreadForm()
	specialty = Specialty.query.get(specialty_id)
	if threadform.validate_on_submit():
		thread = Thread(body=threadform.body.data, author=current_user,title=threadform.title.data,
					specialty=Specialty.query.get(specialty_id))
		db.session.add(thread)
		db.session.commit()
		flash(_('Your thread is now live!'))
		return redirect(url_for('main.threads', specialty_id=specialty_id))
	return render_template('new_thread.html', specialty2 = specialty2, specialty=specialty, threadform=threadform)

@bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
	specialty2 = session.get('specialty')
	page = request.args.get('page', 1, type=int)
	postform = PostForm()
	thread = Thread.query.get(thread_id)
	if postform.validate_on_submit():
		post = Post(body=postform.post.data, author=current_user, thread_id=thread_id)
		db.session.add(post)
		db.session.commit()
		flash(_('Your post is now live!'))
		return redirect(url_for('main.thread', thread_id=thread_id))
	posts = thread.posts.order_by(Post.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.thread', thread_id=thread_id,
					   page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.thread', thread_id=thread_id,
					   page=posts.prev_num) if posts.has_prev else None
	return render_template('thread.html', specialty2 = specialty2, next_url=next_url, prev_url=prev_url, postform=postform, posts=posts.items, thread=thread)

@bp.route('/delete_thread/<int:thread_id>', methods=['GET','POST'])
@login_required
def delete_thread(thread_id):
	thread = Thread.query.get(thread_id)
	if current_user == thread.author:
		db.session.delete(thread)
		db.session.commit()
		flash('Thread deleted!')
	return redirect(request.referrer)

@bp.route('/angulartest')
def angulartest():
	return render_template('angulartest.html')