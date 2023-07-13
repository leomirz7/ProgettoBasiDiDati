import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, send_file, session
from flask_login import *

from website import db
from website.models import User, Project, Document, Report

evaluator = Blueprint('evaluator', __name__)

@evaluator.route('/')
@login_required
def private():
    user = User.query.get(int(current_user.id))
    projects = Project.query.filter(Project.status != 'new')

    return render_template('evaluator.html', user=current_user, user_data=user, projects=projects)


@evaluator.route('/open',  methods=['GET', 'POST'])
@login_required
def open():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

    print(user.username)

    if request.method == 'GET':

        reps = Report.query.filter_by(idDocProj=p_id)

        for r in reps.all():
            print(vars(r))

        for d in docs:
            print(d)
        flag = 1
        render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, docs=docs, reps=reps, flag=flag)
    if request.method == 'POST':
        print("ciao")

    return redirect(url_for('researcher.private'))

@evaluator.route('/download')
@login_required
def download():
    projId = request.args.get('p')
    print(projId)
    proj = Project.query.get(int(projId))
    filename = request.args.get('dName')

    user = User.query.get(int(proj.idRes))

    uploads = f"{os.getcwd()}/files/{user.username}/{proj.id}/{filename}"
    return send_file(uploads)

@evaluator.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    projId = request.args.get('pip')
    print(projId)
    proj = Project.query.get(int(projId))

    docId = request.args.get('did')

    user = User.query.get(int(proj.idRes))

    rep = request.args.get('r')

    if request.method == 'GET':
        return render_template('report.html', user=current_user, user_data=user, p=proj, rep=rep)


    if request.method == 'POST':
        score = request.form.get('score')
        text = request.form.get('text')

        new_report = Report(score=score, text=text, idEval=current_user.id, idDocName=docId, idDocProj=projId)
        db.session.add(new_report)
        db.session.commit()

        return redirect(url_for('evaluator.open', id=projId))

