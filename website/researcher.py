import os
import shutil

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import *

from website import db
from website.models import User, Project, Document

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
            new_doc = Document(idProj=proj.id, name=file.filename)
            db.session.add(new_doc)

            print(os.getcwd())
            file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")

        db.session.commit()
        flash('Progetto creato', category="success")

    return render_template('crea_progetto.html', user=current_user, user_data=user)

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
            new_doc = Document(idProj=proj.id, name=file.filename)
            db.session.add(new_doc)
            file.save(f"{os.getcwd()}/files/{user.username}/{proj.id}/{file.filename}")

        proj.name = name
        proj.description = desc
        proj.status = status

        db.session.commit()
        flash('Progetto aggiornato', category="success")

    return redirect(url_for('researcher.private'))
