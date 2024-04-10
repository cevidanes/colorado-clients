# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
# Import Form Objects
from forms.forms import RegistrationForm, LoginForm
# Import db Models Objects
from models.models import CPUser
# Import authentication module
from authentication.auth import auth
from admin_users.admin_users import admin_users
import os
import json

load_dotenv()

# Import db instance and models
from extensions import db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_SECRET_KEY', 'fallback_secret_key') #ToDo:create secret key inside docker configuration
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin_users, url_prefix='/admin_users')
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

@app.route('/users', methods=['GET', 'POST'])
@login_required
def handle_users():
    if request.method == 'GET':
        users = CPUser.query.all()
        users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]  # Customize based on your model
        return jsonify(users_list)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or not 'username' in data or not 'email' in data or not 'password' in data:
            abort(400)  # Missing information
        user = CPUser(username=data['username'], email=data['email'])
        # Set additional fields and handle password setting appropriately
        db.session.add(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User created successfully"}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = CPUser.query.get_or_404(user_id)
    data = request.get_json()

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    # Update additional fields as necessary

    db.session.commit()
    return jsonify({"success": True, "message": "User updated successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
