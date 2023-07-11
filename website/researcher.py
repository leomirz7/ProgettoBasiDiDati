from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

researcher = Blueprint('researcher', __name__)

@researcher.route('/')
@login_required
def private():
    # return render_template('researcher.html', user=current_user)
    return 'ciao'
