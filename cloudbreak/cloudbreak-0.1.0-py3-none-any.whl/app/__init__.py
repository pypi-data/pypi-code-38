from flask import Flask
from flask_cors import CORS
app = Flask(__name__, static_folder='./dist/static',
            template_folder='./dist')
app.config.from_object('config')
CORS(app)

from app import views
