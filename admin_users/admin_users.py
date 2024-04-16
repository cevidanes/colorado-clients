# admin_users.py
from flask import Blueprint, render_template,abort,jsonify,request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
# Import db Models Objects
from models.models import CPUser
# Import db instance and models
from extensions import db

admin_users = Blueprint('admin_users', __name__, template_folder='templates')

@admin_users.route('/home')
def home():
    return render_template('admin_users/home.html')

@admin_users.route('/users', methods=['GET', 'POST'])
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

@admin_users.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    try:
        user = CPUser.query.get_or_404(user_id)
        data = request.get_json()

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        # Update additional fields as necessary

        db.session.commit()
        return jsonify({"success": True, "message": "Usuário atualizado com sucesso!"})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Um usuário com mesmo nome já existe!"}), 400
    except Exception as e:
        db.session.rollback()
        # Log the exception here
        return jsonify({"success": False, "message": "Ocorreu um erro ao atualizar o usuário. Contate seu administrador."}), 500

@admin_users.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
   # if not current_user.is_admin:  # Assuming you have an 'is_admin' property
    #    abort(403, description="Access denied. Administrator rights required.")

    user = CPUser.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "Usuário deletado com sucesso."}), 200
    except Exception as e:
        db.session.rollback()
        # Log the exception here
        return jsonify({"success": False, "message": "An error occurred while deleting the user."}), 500