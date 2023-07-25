from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, Evaluator, Researcher

from . import db    # prende db da __init__.py

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.pwd, pwd):

                ev = Evaluator.query.get(int(user.id))
                res = Researcher.query.get(int(user.id))

                if ev:
                    login_user(ev, remember=True)
                else:
                    login_user(res, remember=True)


                flash("Logged in!", category='success')
                print(url_for('redirect2.home'))
                return redirect(url_for('redirect2.home'))
            else:
                flash("Password scorretta", category='error')
        else:
            flash("Email does not exist", category='error')

    return render_template('login.html', user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    print("aaa") 
    if request.method == 'POST':
        username = request.form.get('user')
        email = request.form.get('email')
        tipo = request.form.get('tipo')
        pwd = request.form.get('pwd')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exist", category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif len(pwd) < 4:
            flash('Password must be at least 4 characters.', category='error')
        elif tipo != 'Researcher' and tipo != 'Evaluator':
            flash('Inserire un tipo', category='error')
        else:
            new_user = User(username=username, email=email, pwd=generate_password_hash(pwd, method='scrypt'))
            db.session.add(new_user)

            user = User.query.filter_by(email=email).first()


            if tipo == 'Researcher':
                new_child = Researcher(user.id)
            else:
                new_child = Evaluator(user.id)

            db.session.add(new_child)
            db.session.commit()
            login_user(new_child, remember=True)
            flash("Account creato", category="success")

            return redirect(url_for('redirect2.home'))

    return render_template('register.html', user=current_user)


@auth.route('/logout')
@login_required     # richiede autenticazione
def logout():
    logout_user()   # chiamata a Flask - L
    return redirect(url_for('auth.login'))
