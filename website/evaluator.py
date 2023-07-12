from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

evaluator = Blueprint('evaluator', __name__)

@evaluator.route('/')
@login_required
def private():
    return render_template('evaluator.html', user=current_user)
    return 'ciao 2'
