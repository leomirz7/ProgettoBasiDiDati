from datetime import date, timedelta
import os
import shutil

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

from website import db
from website.models import Report, Status, User, Project, Document
from website.util import restrict_user
from .util import results

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
        db.session.commit()

        os.makedirs(f"{os.getcwd()}/files/{user.id}/{new_proj.id}/")
        for file in files:
            """ print("\n\n\n\n\n")
            print(os.path.splitext(file.filename))
            print("\n\n\n\n\n") """
            new_doc = Document(idProj=new_proj.id, name=file.filename,type=os.path.splitext(file.filename)[1].replace(".",""))
            db.session.add(new_doc)

            print(os.getcwd())
            file.save(f"{os.getcwd()}/files/{user.id}/{new_proj.id}/{file.filename}")

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
    proj = Project.query.get_or_404(p_id)
    if(proj.idRes != user.id):
        return render_template('401.html')

    result = results(p_id)
    return render_template('visualizza_progetto.html', user=current_user, user_data=user, p=proj, q=result, os = os)



def checkIfEdit(proj, docs):
    f = False
    for doc in docs:
        print("aadfad", doc.status)
        if(doc.status.value == "changes_request"):
            f = True
    print(f"flag {f}")
    if(f == False and proj.status.value != "new"):
        proj.status = "pending"
    db.session.commit()
    return proj.status


@researcher.route('/delete',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def delete():
    p_id = request.args.get('id')
    print(p_id)
    proj = Project.query.get_or_404(p_id)

    user = User.query.get(int(current_user.id))
    docs = Document.query.filter_by(idProj=p_id)

    shutil.rmtree(f"{os.getcwd()}/files/{user.id}/{proj.id}/")

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
    proj = Project.query.get_or_404(p_id)

    user = User.query.get(int(current_user.id))
    doc = Document.query.filter_by(idProj=p_id, name = d_id).first()
    docs = Document.query.filter_by(idProj=p_id)
    
    os.remove(f"{os.getcwd()}/files/{user.id}/{proj.id}/{doc.name}")
    db.session.delete(doc)
    checkIfEdit(proj, docs)
    

    flash("Documento cancellato!", category="success")
    return redirect(url_for('researcher.open',id=p_id))


@researcher.route('/editDoc',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def editDoc():
    p_id = request.args.get('pip')
    d_id = request.args.get('did')
    user = User.query.get(int(current_user.id))
    proj = Project.query.get_or_404(p_id)
    doc_old = Document.query.filter_by(idProj=p_id, name = d_id).first()
    rep = Report.query.filter_by(idDocName=d_id, idDocProj=p_id).first()

    if request.method == 'GET':
        return render_template('modifica_documento.html', user=current_user, user_data=user, doc=doc_old)
    if request.method == 'POST':
        file = request.files.get('files')
        type = request.form.get('type')
    
    if file.filename:
        doc = Document.query.filter_by(idProj=p_id, name = file.filename).first()
        if not doc:
            os.remove(f"{os.getcwd()}/files/{user.id}/{proj.id}/{doc_old.name}")
            db.session.delete(doc_old)
            db.session.delete(rep)

            new_doc = Document(idProj=proj.id, name=file.filename, type=type, status="default")
            file.save(f"{os.getcwd()}/files/{user.id}/{proj.id}/{file.filename}")
            db.session.add(new_doc)
            db.session.commit()
            
            print(os.getcwd())
            file.save(f"{os.getcwd()}/files/{user.id}/{proj.id}/{file.filename}")
            
            flash("Documento modificato!", category="success")
            
            docs = Document.query.filter_by(idProj=p_id)
            checkIfEdit(proj, docs)
            db.session.commit()
        else:
            flash(f"Il file {file.filename} è già presente", category="error")
 
    return redirect(url_for('researcher.open',id=p_id))


@researcher.route('/edit',  methods=['GET', 'POST'])
@login_required
@restrict_user(current_user, ['Researcher'])
def edit():
    user = User.query.get(int(current_user.id))
    p_id = request.args.get('id')
    proj = Project.query.get_or_404(p_id)
    docs = Document.query.filter_by(idProj=p_id)


    if request.method == 'GET':
        return render_template('modifica_progetto.html', user=current_user, user_data=user, proj=proj, docs=docs)
    
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        status = request.form.get('status')

        files = request.files.getlist('files')

        print(request.values)

        for file in files:
            if file.filename:
                doc = Document.query.filter_by(idProj=p_id, name = file.filename).first()
                if not doc:
                    new_doc = Document(idProj=proj.id, status="default", name=file.filename, type=os.path.splitext(file.filename)[1].replace(".",""))
                    db.session.add(new_doc)

                    file.save(f"{os.getcwd()}/files/{user.id}/{proj.id}/{file.filename}")
                else:
                    flash(f"Il file {file.filename} è già presente", category="error")

        proj.name = name
        proj.description = desc
        db.session.commit()

        nDocs = Document.query.filter_by(idProj=p_id).count()
        if(status):
            if(nDocs == 0):
                flash('Non pubblicato, non ci sono documenti', category="error")
            else :
                proj.status = "pending"
                proj.endDate = date.today() + timedelta(days=30)
                db.session.commit()
                flash('Progetto pubblicato', category="success")
                return redirect(url_for('researcher.private'))

        flash('Progetto salvato', category="success")

    return redirect(url_for('researcher.edit', id=p_id))
