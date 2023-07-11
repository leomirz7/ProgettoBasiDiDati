from os import path
from flask import Flask
from flask_login import *
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ubersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .auth import auth
    from .researcher import researcher
    from .evaluator import evaluator
    from .redirect import redirect

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(redirect)
    app.register_blueprint(researcher)
    app.register_blueprint(evaluator)

    from .models import User
    from .models import Evaluator
    from .models import Researcher

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        ev = Evaluator.query.get(int(id))
        res = Researcher.query.get(int(id))

        if ev:
            return ev
        else:
            return res

        # return User.query.get(int(id))


    return app



def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

