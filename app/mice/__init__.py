from flask import Blueprint

bp = Blueprint('mice', __name__)

from app.mice import routes