from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, BooleanField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length, Optional, NumberRange
from flask_babel import _, lazy_gettext as _l
from app.models import User
from wtforms.fields.html5 import DateField
from wtforms.widgets import HiddenInput

class EmptyForm(FlaskForm):
	submit = SubmitField('Submit')

class PostForm(FlaskForm):
	body = TextAreaField(_l('Enter post:'), validators=[DataRequired()])
	submit = SubmitField(_l('Submit'))

class SLUMSForm(FlaskForm):
	day = StringField('What day of the week is it?')
	year = StringField('What is the year?')
	state = StringField('What state are we in?')
	objects = StringField('Please remember these five objects. I will ask you what they are later.')
	submit = SubmitField('Submit')