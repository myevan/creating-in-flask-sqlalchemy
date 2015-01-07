from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()


class Device(db.Model):
    __bind_key__ = 'global_db'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guid = db.Column(db.String(32), unique=True)


class User(db.Model):
    __bind_key__ = 'user_db'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User {0}>'.format(self.username)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_BINDS'] = {
        'global_db': 'sqlite:///temp/global_db.sq3',
        'user_db': 'sqlite:///temp/user_db.sq3',
    }

    if not os.access('temp', os.R_OK):
        os.makedirs('temp')

    db.init_app(app)
    db.create_all(app=app)
    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.session.add(User(username='admin', email='admin@example.com'))
        db.session.commit()
