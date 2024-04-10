# admin_users.py
from flask import Blueprint, render_template

admin_users = Blueprint('admin_users', __name__, template_folder='templates')

@admin_users.route('/home')
def home():
    return render_template('admin_users/home.html')