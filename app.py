# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
# Import Form Objects
from forms.forms import RegistrationForm, LoginForm
# Import db Models Objects
from models.users.users import CPUser
# Import authentication module
from authentication.auth import auth
from admin_users.admin_users import admin_users
from contracts.contracts import contracts
import os
import json

load_dotenv()

# Import db instance and models
from utilities.extensions import db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_SECRET_KEY', 'fallback_secret_key') #ToDo:create secret key inside docker configuration
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin_users, url_prefix='/admin_users')
app.register_blueprint(contracts, url_prefix='/contracts')
# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # The name of the view to redirect to when the user needs to log in.

# Database configuration from environment variables or default
DB_NAME = os.getenv('DB_NAME', 'colorado_clients')
DB_USER = os.getenv('DB_USER', 'colorado')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'colorado123')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@login_manager.user_loader
def load_user(id):
    return CPUser.query.get(int(id))

# Initialize SQLAlchemy and Migrate with app
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
     return redirect(url_for('auth.login') )

@app.route('/index')
def indexx():
     return render_template('dashboard.html', title='Home Page')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
