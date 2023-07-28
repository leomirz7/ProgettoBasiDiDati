from functools import wraps
import os

from flask import Blueprint, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from website.models import Project, Report, User

def restrict_user(current_user, user_type):
    def decorator(route_function):
        @wraps(route_function)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.__class__.__name__ in str(user_type):
                return redirect(url_for('static', filename= "401.html"))
            return route_function(*args, **kwargs)
        return decorated_function
    return decorator

util = Blueprint('util', __name__)

@util.route('/report',  methods=['GET', 'POST'])
@login_required

def report():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))
    docId = request.args.get('did')
    user = User.query.get(int(proj.idRes))
    rep = request.args.get('r')

    report = Report.query.get(rep)

    if request.method == 'GET':
        return render_template('reportRes.html', user=current_user, user_data=user, p=proj, rep=report)

@util.route('/download')
@login_required
def download():
    projId = request.args.get('p')
    print(projId)
    proj = Project.query.get(int(projId))
    filename = request.args.get('dName')

    user = User.query.get(int(proj.idRes))

    uploads = f"{os.getcwd()}/files/{user.username}/{proj.id}/{filename}"
    return send_file(uploads)