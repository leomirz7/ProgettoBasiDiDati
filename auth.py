from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # return redirect(url_for('researcher.private'))  # per andare dal ricercatore
    return "pagina di login"


@auth.route('/logout')
@login_required     # richiede autenticazione
def logout():
    logout_user()   # chiamata a Flask - L