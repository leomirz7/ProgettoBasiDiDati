from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/users/<username>')
def show_profile(username):
    users = ['alice', 'bob', 'charlie']
    if username in users:
        return render_template('profile.html', user=username)
    else :
        return render_template('profile.html')
