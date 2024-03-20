from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from celery import Celery
from uni_rlhf.models import db
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-CORS configuration
cors = CORS(app, supports_credentials=True)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Application Secret Key
app.secret_key = 'your_secret_key'

BASE_URL = "./uni_rlhf/vue_part/src/assets/video/"
UPLOAD_DATASETS_URL = './uni_rlhf/datasets/temp_datasets'
EXPORTED_PROJECT_URL = os.path.join(os.getcwd(), 'uni_rlhf/datasets/temp_datasets')



