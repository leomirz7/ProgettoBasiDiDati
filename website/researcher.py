from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

researcher = Blueprint('researcher', __name__)

@researcher.route('/researcher')
@login_required
def private():
    print("researcher private")
    return "pagina del ricercatore"