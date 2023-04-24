from flask import Flask, render_template, redirect, url_for, request

from flask_login import *

app = Flask(__name__)

app = Flask( __name__ )
app.config['SECRET_KEY'] = 'ubersecret'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/users/<username>')
def show_profile(username):
    users = ['alice', 'bob', 'charlie']
    if username in users:
        return render_template('profile.html', user=username)
    else:
        return render_template('profile.html', reg=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = request.form["user"]
    return redirect(url_for('show_profile', username=user))
