from datetime import date, timedelta
import os
import shutil

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

from website import db
from website.models import Report, Status, User, Project, Document
from website.util import restrict_user

researcher = Blueprint('researcher', __name__)

@researcher.route('/')
@login_required
@restrict_user(current_user, ['Researcher'])
def private():
    user = User.query.get(int(current_user.id))
    projects = Project.query.filter_by(idRes=current_user.id).all()
    for p in projects:
        if p.endDate and p.endDate < date.today():
            """ print(p.status) """
            p.status = "new"
            """ print(p.status) """

    db.session.commit()

    return render_template('researcher.html', user=current_user, user_data=user, projects=projects)


@researcher.route('/create',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def create():
    user = User.query.get(int(current_user.id))
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        files = request.files.getlist('files')

        

        new_proj = Project(description=desc, name=name, idRes=current_user.id)
        db.session.add(new_proj)

        proj = Project.query.filter_by(description=desc, name=name, idRes=current_user.id).first()

        os.makedirs(f"{os.getcwd()}/files/{user.username}/{proj.id}/")
        for file in files:
            """ print("\n\n\n\n\n")
            print(os.path.splitext(file.filename))
            print("\n\n\n\n\n") """
            new_doc = Document(idProj=proj.id, name=file.filename,type=os.path.splitext(file.filename)[1].replace(".",""))
            db.session.add(new_doc)

            print(os.getcwd())
            file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")

        db.session.commit()
        flash('Progetto creato', category="success")
        return redirect(url_for('researcher.private'))
    return render_template('crea_progetto.html', user=current_user, user_data=user)


@researcher.route('/open',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def open():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

    reps = Report.query.filter_by(idDocProj=p_id)
    """ for r in reps:
        print(r) """
    q = db.session.query(Report, Document).join(Report, Document.name == Report.idDocName and Document.idProj == Report.idDocProj, isouter=True).filter(Document.idProj == p_id).all()
    """ for d in q:
        print(d) """
    if request.method == 'GET':
        return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=q, os = os)
    # if request.method == 'POST':
    #     print("ciao")
    return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=q, os = os)


def checkIfEdit(proj, docs):
    f = False
    for doc in docs:
        if(doc.status == "changes_request"):
            f = True
    if(f == False and proj.status.value != "new"):
        proj.status = "pending"
    return "asds"


@researcher.route('/delete',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def delete():
    p_id = request.args.get('id')
    print(p_id)
    proj = Project.query.get(p_id)

    user = User.query.get(int(current_user.id))
    docs = Document.query.filter_by(idProj=p_id)

    shutil.rmtree(f"{os.getcwd()}/files/{user.username}/{proj.id}/")

    for doc in docs:
        db.session.delete(doc)

    db.session.delete(proj)
    db.session.commit()
    flash("Progetto cancellato!", category="success")
    return redirect(url_for('researcher.private'))

@researcher.route('/deleteDoc',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def deleteDoc():
    p_id = request.args.get('pip')
    d_id = request.args.get('did')
    proj = Project.query.get(p_id)

    user = User.query.get(int(current_user.id))
    doc = Document.query.filter_by(idProj=p_id, name = d_id).first()
    docs = Document.query.filter_by(idProj=p_id)
    
    os.remove(f"{os.getcwd()}/files/{user.username}/{proj.id}/{doc.name}")
    db.session.delete(doc)
    checkIfEdit(proj, docs)
    db.session.commit()

    flash("Documento cancellato!", category="success")
    return redirect(url_for('researcher.open',id=p_id))


@researcher.route('/editDoc',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def editDoc():
    p_id = request.args.get('pip')
    d_id = request.args.get('did')
    user = User.query.get(int(current_user.id))
    proj = Project.query.get(p_id)
    doc = Document.query.filter_by(idProj=p_id, name = d_id).first()
    docs = Document.query.filter_by(idProj=p_id)
    rep = Report.query.filter_by(idDocName=d_id, idDocProj=p_id).first()


    if request.method == 'GET':
        return render_template('modifica_documento.html', user=current_user, user_data=user, doc=doc)
    if request.method == 'POST':
        file = request.files.get('files')
        type = request.form.get('type')
    
    os.remove(f"{os.getcwd()}/files/{user.username}/{proj.id}/{doc.name}")
    db.session.delete(doc)
    db.session.delete(rep)
    
    new_doc = Document(idProj=proj.id, name=file.filename, type=type, status="default")
    db.session.add(new_doc)
    print(os.getcwd())
    file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")
    
    checkIfEdit(proj, docs)
    db.session.commit()
 
    flash("Documento modificato!", category="success")
    return redirect(url_for('researcher.open',id=p_id))


@researcher.route('/edit',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def edit():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

    print(proj.status)


    if request.method == 'GET':
        return render_template('modifica_progetto.html', user=current_user, user_data=user, proj=proj, docs=docs)
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        status = request.form.get('status')
        files = request.files.getlist('files')
        


        # os.makedirs(f"{os.getcwd()}/files/{user.username}/{p_id}/")



        for file in files:
            if file.filename:
                doc = Document.query.filter_by(idProj=p_id, name = file.filename).first()
                if not doc:
                    new_doc = Document(idProj=proj.id, name=file.filename, type=os.path.splitext(file.filename)[1].replace(".",""))
                    db.session.add(new_doc)
                    file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")
                else:
                    print(doc.name)
                    flash(f"Il file {file.filename} è già presente", category="error")

        proj.name = name
        proj.description = desc
        print(proj.status)
        if(status):
            proj.status = status
            proj.endDate = date.today() + timedelta(days=30)

        db.session.commit()
        flash('Progetto aggiornato', category="success")

    return redirect(url_for('researcher.private'))


@researcher.route('/report',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def report():
    projId = request.args.get('pip')
    proj = Project.query.get(int(projId))
    docId = request.args.get('did')
    user = User.query.get(int(proj.idRes))
    rep = request.args.get('r')

    report = Report.query.get(rep)

    if request.method == 'GET':
        return render_template('reportRes.html', user=current_user, user_data=user, p=proj, rep=report)
