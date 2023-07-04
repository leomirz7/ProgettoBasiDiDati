from flask import Flask, render_template, redirect, url_for, request, make_response, blueprints
from flask_login import *
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ubersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)



from auth import auth
from researcher import researcher
from evaluator import evaluator
from redirect import redirect
from models import User

with app.app_context():
    db.create_all()


app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(researcher)
app.register_blueprint(evaluator)
app.register_blueprint(redirect)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

