from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

redirect = Blueprint('redirect', __name__)

@redirect.route('/')
@login_required
def home():
    # current_user identifica l’utente attuale
    # utente anonimo prima dell’ autenticazione
    if current_user.__class__.__name__ == 'Researcher':
        return redirect(url_for('researcher.private'))
    if current_user.__class__.__name__ == 'Evaluator':
        return redirect(url_for('evaluator.private'))
