from . import db
from flask_login import *
from sqlalchemy import  func
import enum

# le tabelle:


class User(db.Model):
    __table_name__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    pwd = db.Column(db.String(150))
    # tipo = db.Column(db.String(64))

    researcher = db.relationship('Researcher', backref='user', uselist=False)
    evaluator = db.relationship('Evaluator', backref='user', uselist=False)

    # __mapper_args__ = {
    #     'polymorphic_identity': 'user',
    #     'polymorphic_on': 'tipo'
    # }


class Status(enum.Enum):
    APPROVED = 'approved'
    PENDING = 'pending'
    CHANGES_REQUEST = 'changes_request'
    REJECTED = 'rejected'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000))
    status = db.Column(
        db.Enum(Status, values_callable=lambda obj: [
            e.value for e in obj]),
        nullable=False,
        default=Status.PENDING.value,
        server_default=Status.PENDING.value
    )
    idRes = db.Column(db.Integer, db.ForeignKey('researcher.id'))

    # __mapper_args__ = {
    #     'polymorphic_identity': 'project'
    # }


class Researcher(db.Model, UserMixin):
    # __table_name__ = "researcher"

    def __init__(self, id):
        self.id = id

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project = db.relationship('Project', backref='researcher')

    # __mapper_args__ = {
    #     'polymorphic_identity': 'researcher'
    # }


class Evaluator(db.Model, UserMixin):
    def __init__(self, id):
        self.id = id

    __table_name__ = "evaluator"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    report = db.relationship('Report', backref='evaluator')

    # __mapper_args__ = {
    #     'polymorphic_identity': 'evaluator'
    # }


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    idEval = db.Column(db.Integer, db.ForeignKey('evaluator.id'))

    idDoc = db.Column(db.Integer, db.ForeignKey('document.id'))

    # __mapper_args__ = {
    #     'polymorphic_identity': 'report'
    # }


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(150))
    report = db.relationship('Report', backref='document')

    # __mapper_args__ = {
    #     'polymorphic_identity': 'document'
    # }