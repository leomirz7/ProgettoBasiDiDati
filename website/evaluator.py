from datetime import date
import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, send_file, session
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

    return render_template('evaluator.html', user=current_user, user_data=user, projects=projects)


@evaluator.route('/open',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def open():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

    reps = Report.query.filter_by(idDocProj=p_id)
    """ for r in reps:
        print(r) """


    # q = Report.query \
    #     .join(Document, Document.name == Report.idDocName) \
    #     .filter(Document.idProj == p_id, Document.idProj == Report.idDocProj).all()

    # q = db.session.query(Document, Report).filter(Document.name == Report.idDocName and Document.idProj == Report.idDocProj and Document.idProj == p_id).all()


    q = db.session.query(Report, Document).join(Report, Document.name == Report.idDocName and Document.idProj == Report.idDocProj, isouter=True).filter(Document.idProj == p_id).all()

    """ for d in q:
        print(d) """

    if request.method == 'GET':

        return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=q, os = os)
    # if request.method == 'POST':
    #     print("ciao")

    return redirect(url_for('evaluator.open'))


@evaluator.route('/download')
@login_required
@restrict_user(current_user, ['Evaluator', 'Researcher'])
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
@restrict_user(current_user, ['Evaluator'])
def report():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))

    docId = request.args.get('did')

    user = User.query.get(int(proj.idRes))

    rep = request.args.get('r')

    report = Report.query.get(rep)

    if request.method == 'GET':
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
    user = User.query.get(int(proj.idRes))
    docs = Document.query.filter_by(idProj=projId, name = docId).first()
    docs.status = "changes_request"
    proj.status = "changes_request"
    db.session.commit()
    return redirect(url_for('evaluator.open', id=projId))



@evaluator.route('/evaluate',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def evaluate():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

    reps = Report.query.filter_by(idDocProj=p_id)
 
    q = db.session.query(Report, Document).join(Report, Document.name == Report.idDocName and Document.idProj == Report.idDocProj, isouter=True).filter(Document.idProj == p_id).all()
    media = 0
    i = 0
    for tupla in q:
        if(tupla[0] == None):
            flash("Non tutti i documenti sono stati valutati", category='error')
            return redirect(url_for('redirect2.home'))
        media += tupla[0].score 
        i += 1
    if(media/i >= 18):
        proj.status = "approved"
        flash("Progetto approvato", category='success')
    else:
        proj.status = "rejected"
        flash("Progetto rifiutato", category='error')
    db.session.commit()
    return redirect(url_for('redirect2.home'))

    
@evaluator.route('/viewReport',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Evaluator'])
def viewReport():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))
    docId = request.args.get('did')
    user = User.query.get(int(proj.idRes))
    rep = request.args.get('r')

    report = Report.query.get(rep)

    if request.method == 'GET':
        return render_template('reportRes.html', user=current_user, user_data=user, p=proj, rep=report)
