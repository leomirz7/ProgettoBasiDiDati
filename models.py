from prova import db
from flask_login import *
from sqlalchemy import  func
import enum


# le tabelle:

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    pwd = db.Column(db.String(150))
    type = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'type'
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