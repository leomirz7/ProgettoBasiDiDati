from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from . import db    # prende db da __init__.py

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(email=email).first()
        if user:
            print(email)
            print(user.pwd)
            print(pwd)
            if check_password_hash(user.pwd, pwd):
                login_user(user, remember=True)
                flash("logged in!", category='success')
                return redirect(url_for('redirect.home'))
            else:
                flash("Password scorretta", category='error')
        else:
            flash("Email does not exist", category='error')

    return render_template('login.html', user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('user')
        email = request.form.get('email')
        tipo = request.form.get('tipo')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(email=email).first()
        # controlli lunghezza e cose varie
        # TODO per far vedere i flash, fare base.html come nel video
        if user:
            print("no")
            flash("email already exist", category='error')
        elif len(email) < 4:
            print("noooo")
            flash("email too short", category="error")
        else:
            new_user = User(username=username, email=email, pwd=generate_password_hash(pwd, method='sha256'), tipo=tipo)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account creato", category="success")
            print("si")
            return redirect(url_for('redirect.home'))

    return render_template('register.html', user=current_user)


@auth.route('/logout')
@login_required     # richiede autenticazione
def logout():
    logout_user()   # chiamata a Flask - L
    return redirect(url_for('auth.login'))
