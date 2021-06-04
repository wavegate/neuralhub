from app import db, csrf
from app.mice import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
import datetime as dt
from app.models import User, Mouse
from sqlalchemy import nulls_last

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	return render_template('mice/index.html')

@bp.route('/mice', methods=['GET', 'POST'])
@login_required
def mice():
	return render_template('mice/mice.html', mice=Mouse.query.filter_by(user_id=current_user.id))

@bp.route("/mice/<int:id>", methods = ['GET'])
@login_required
def mouse(id):
	mouse = Mouse.query.get(id)
	return render_template('mice/mouse.html', mouse=mouse)

@bp.route("/add_mouse", methods = ['GET', 'POST'])
@login_required
@csrf.exempt
def add_mouse():
	last_mouse = Mouse.query.filter_by(user_id=current_user.id).order_by(nulls_last(Mouse.timestamp.desc())).limit(1).all()
	if last_mouse:
		last_mouse = last_mouse[0]
	if request.method == 'POST':
		date_in = request.form.get('dob')
		date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
		date_processing = [int(v) for v in date_processing]
		date_out = dt.datetime(*date_processing)
		mouse = Mouse(dob=date_out, sex=request.form.get('sex'), notes=request.form.get('editordata'), genotype=request.form.get('genotype'), cagetag=request.form.get('cagetag'), owner=current_user)
		db.session.add(mouse)
		db.session.commit()
		return redirect(url_for('mice.mice'))
	if last_mouse:
		return render_template('mice/add_mouse.html', mouse=last_mouse, dob=last_mouse.dob.strftime("%Y-%m-%dT%H:%M"))
	else:
		return render_template('mice/add_mouse.html')

@bp.route("/edit_mouse/<int:id>", methods = ['GET', 'POST'])
@login_required
@csrf.exempt
def edit_mouse(id):
	mouse = Mouse.query.get(id)
	if request.method == 'POST':
		date_in = request.form.get('dob')
		date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
		date_processing = [int(v) for v in date_processing]
		date_out = dt.datetime(*date_processing)
		mouse.dob = date_out
		mouse.sex = request.form.get('sex')
		mouse.notes = request.form.get('editordata')
		mouse.genotype = request.form.get('genotype')
		mouse.cagetag = request.form.get('cagetag')
		db.session.commit()
		return redirect(url_for('mice.mouse', id=mouse.id))
	return render_template('mice/edit_mouse.html', mouse=mouse, dob=mouse.dob.strftime("%Y-%m-%dT%H:%M"))

@bp.route("/remove_mouse/<int:id>", methods = ['GET', 'POST'])
@login_required
def remove_mouse(id):
	mouse = Mouse.query.get(id)
	db.session.delete(mouse)
	db.session.commit()
	return redirect(url_for('mice.mice'))


#class Mouse(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	sex = db.Column(db.Integer)
#	genotype = db.Column(db.String(500))
#	dob = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#	cage = db.Column(db.Integer, db.ForeignKey('cage.id'))
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	notes = db.Column(db.Text)
#
#class Cage(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	tag = db.Column(db.String(500))
#	mice = db.relationship('Mouse', backref='house', lazy='dynamic')
#	notes = db.Column(db.Text)
#	mouseline = db.Column(db.String(500))
#	setup_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@bp.route('/cages', methods=['GET', 'POST'])
@login_required
def cages():
	return render_template('mice/cages.html')


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