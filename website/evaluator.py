from datetime import date
import os

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

from website import db
from website.models import User, Project, Document, Report

from .util import *

evaluator = Blueprint('evaluator', __name__)


@evaluator.route('/')
@login_required
@restrict_user(current_user, ['Evaluator'])
def private():
    user = User.query.get(int(current_user.id))
    projects = Project.query.filter(Project.status != 'new' and Project.endDate >= date.today()).all()
    for p in projects:
        print(f"grade: {p.grade}, name {p.name}")
    return render_template('evaluator.html', user=current_user, user_data=user, projects=projects)


@evaluator.route('/open',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def open():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    result = results(p_id)

    return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=result, os = os)



@evaluator.route('/report', methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def report():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))

    docId = request.args.get('did')

    user = User.query.get(int(proj.idRes))

    rep = request.args.get('r')


    if request.method == 'GET':
        report = Report.query.get(rep)
        return render_template('report.html', user=current_user, user_data=user, p=proj, rep=report)

    if request.method == 'POST':
        score = request.form.get('score')
        text = request.form.get('text')

        if rep:
            reps = Report.query.filter_by(id=rep).first()
            reps.text = text
            reps.score = score
        else:
            new_report = Report(score=score, text=text, idEval=current_user.id, idDocName=docId, idDocProj=projId)
            db.session.add(new_report)
        db.session.commit()

        return redirect(url_for('evaluator.open', id=projId))


@evaluator.route('/requestC', methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def requestC():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))
    docId = request.args.get('did')
    docs = Document.query.filter_by(idProj=projId, name = docId).first()

    docs.status = "changes_request"
    proj.status = "changes_request"

    db.session.commit()
    return redirect(url_for('evaluator.open', id=projId))


@evaluator.route('/evaluate', methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def evaluate():
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)

    result = results(p_id)
    media = 0
    i = 0

    for r,_ in result:
        if(r == None or proj.status.value == "changes_request"):
            flash("Non tutti i documenti sono stati valutati", category='error')
            return redirect(url_for('evaluator.private'))
        media += r.score 
        i += 1
    if i == 0:
        flash("Non ci sono documenti da valutare", category='error')
        return redirect(url_for('evaluator.private'))
    proj.grade = media/i
    if(media/i >= 18):
        proj.status = "approved"
        flash("Progetto approvato", category='success')
    else:
        proj.status = "rejected"
        flash("Progetto rifiutato", category='error')
    db.session.commit()
    return redirect(url_for('evaluator.private'))
