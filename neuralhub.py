from flask import Flask
neuralhub = Flask(__name__)

@neuralhub.route('/')
def index():
	return 'Hello World!'