from os import getenv
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
import dateutil
from dotenv import load_dotenv

# local dependencies
from .client import TripClient

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
client = TripClient()
load_dotenv()

# blueprints
from .users.routes import users
from .trips.routes import trips

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = getenv("SECRET_KEY")
    app.config['MONGODB_HOST'] = getenv("MONGODB_HOST")
    app.config['WMATA_KEY'] = getenv("WMATA_KEY")

    # init clients
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # init blueprints
    app.register_blueprint(users)
    app.register_blueprint(trips)
    # TODO app.register_error_handler()

    login_manager.login_view = 'users.login'

    return app
