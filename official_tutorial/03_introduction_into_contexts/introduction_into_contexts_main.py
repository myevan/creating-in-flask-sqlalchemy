from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User {0}>'.format(self.username)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    db.init_app(app)
    db.create_all(app=app)
    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.session.add(User(username='admin', email='admin@example.com'))
        db.session.commit()
