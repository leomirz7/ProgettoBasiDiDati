from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

evaluator = Blueprint('evaluator', __name__)

@evaluator.route('/evaluator')
@login_required
def private():
    return "pagina del valutatore"