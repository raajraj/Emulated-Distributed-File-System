from flask import Flask, render_template

from firebase_api import firebase_api
from mysql_api import mysql_api

UPLOAD_FOLDER = './uploads'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(mysql_api)
app.register_blueprint(firebase_api)


@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/firebase')
def firebase():
    return render_template("firebase.html")


@app.route('/mysql')
def mysql():
    return render_template("mysql.html")


@app.route('/explanation')
def explanation():
    return render_template("explanation.html")



if __name__ == '__main__':
    app.run(debug=True, port=5432)
