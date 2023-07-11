from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *
from .models import User, Evaluator, Researcher
from . import db


redirect2 = Blueprint('redirect2', __name__)


@redirect2.route('/')
@login_required
def home():
    # print(current_user.__class__.__name__)
    #
    # if current_user.__class__.__name__ == 'Researcher':
    #     return redirect(url_for('researcher.private'))
    # if current_user.__class__.__name__ == 'Evaluator':
    #     redirect(url_for('evaluator.private'))
    #
    # # return render_template('researcher.html', user=current_user)
    #
    # print(url_for('researcher.private'))
    #
    return redirect(url_for('researcher.private'))
