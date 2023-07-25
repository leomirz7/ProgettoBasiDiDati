import os
import shutil

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

from website import db
from website.models import Report, User, Project, Document

researcher = Blueprint('researcher', __name__)

@researcher.route('/')
@login_required
def private():
    user = User.query.get(int(current_user.id))
    projects = Project.query.filter_by(idRes=current_user.id)

    return render_template('researcher.html', user=current_user, user_data=user, projects=projects)

@researcher.route('/create',  methods=['GET', 'POST'])
@login_required
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
            print("\n\n\n\n\n")
            print(os.path.splitext(file.filename))
            print("\n\n\n\n\n")
            new_doc = Document(idProj=proj.id, name=file.filename,type=os.path.splitext(file.filename)[1])
            db.session.add(new_doc)

            print(os.getcwd())
            file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")

        db.session.commit()
        flash('Progetto creato', category="success")
        return redirect(url_for('researcher.private'))
    return render_template('crea_progetto.html', user=current_user, user_data=user)


@researcher.route('/open',  methods=['GET', 'POST'])
@login_required
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
        return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=q)
    # if request.method == 'POST':
    #     print("ciao")
    return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=q)


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
    return redirect(url_for('researcher.private'))

@researcher.route('/editDoc',  methods=['GET', 'POST'])
@login_required
def editDoc():
    p_id = request.args.get('pip')
    d_id = request.args.get('did')
    user = User.query.get(int(current_user.id))
    proj = Project.query.get(p_id)
    doc = Document.query.filter_by(idProj=p_id, name = d_id).first()
    docs = Document.query.filter_by(idProj=p_id)

    if request.method == 'GET':
        return render_template('modifica_documento.html', user=current_user, user_data=user, doc=doc)
    if request.method == 'POST':
        file = request.files.get('files')
        type = request.form.get('type')
    
    os.remove(f"{os.getcwd()}/files/{user.username}/{proj.id}/{doc.name}")
    db.session.delete(doc)
    
    new_doc = Document(idProj=proj.id, name=file.filename, type=type)
    db.session.add(new_doc)
    print(os.getcwd())
    file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")
    
    checkIfEdit(proj, docs)
    db.session.commit()
 
    flash("Documento modificato!", category="success")
    return redirect(url_for('researcher.open',id=p_id))

@researcher.route('/edit',  methods=['GET', 'POST'])
@login_required
def edit():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get(p_id)
    docs = Document.query.filter_by(idProj=p_id)

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
                new_doc = Document(idProj=proj.id, name=file.filename)
                db.session.add(new_doc)
                file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")

        proj.name = name
        proj.description = desc
        if(status):
            proj.status = status

        db.session.commit()
        flash('Progetto aggiornato', category="success")

    return redirect(url_for('researcher.private'))
