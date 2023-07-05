from . import db
from flask_login import *
from sqlalchemy import  func
import enum


# le tabelle:

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    pwd = db.Column(db.String(150))
    tipo = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        # 'polymorphic_on': 'tipo'
    }


class Researcher(User):
    __table_name__ = "researcher"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'researcher'
    }


class Evaluator(User):
    __table_name__ = "evaluator"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'evaluator'
    }


class Status(enum.Enum):
    APPROVED = 'approved'
    PENDING = 'pending'
    CHANGES_REQUEST = 'changes_request'
    REJECTED = 'rejected'


class Project:
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


class Report:
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    idEval = db.Column(db.Integer, db.ForeignKey('evaluator.id'))

    idDoc = db.Column(db.Integer, db.ForeignKey('document.id'))

    # __mapper_args__ = {
    #     'polymorphic_identity': 'report'
    # }


class Document:
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(150))

    # __mapper_args__ = {
    #     'polymorphic_identity': 'document'
    # }