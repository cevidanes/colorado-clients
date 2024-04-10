# auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from forms.forms import LoginForm, RegistrationForm
from models.models import CPUser
from extensions import db
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect to the main page if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = CPUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_users.home'))
        else:
            flash('Falha no login. Por favor, verifique seu usuário e senha', 'danger')  # Login failure message in Portuguese
    return render_template('/authentication/login.html', title='Entrar', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Você saiu com sucesso.')  # "You have successfully logged out." in Portuguese
    return redirect(url_for('auth.login'))  # Redirecting to the login page after logout


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate():
        user = CPUser(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Solicitação enviada. Aguarde a aprovação para acessar a ferramenta!', 'success')
            #return redirect(url_for('login'))  # Assuming you have a login route
        except IntegrityError:
            db.session.rollback()  # Roll back the session to a clean state
            flash('Usuário ou email já cadastrado.', 'error')  # Inform the user about the error
    return render_template('/authentication/register.html', title='Register', form=form)

# Continue with other authentication routes...
