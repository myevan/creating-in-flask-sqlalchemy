from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    addresses = db.relationship(lambda: Address, backref=db.backref('person', lazy='joined'), lazy='dynamic')


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    person_id = db.Column(db.Integer, db.ForeignKey(Person.id))


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)
    db.create_all(app=app)
    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        new_person = Person(name='A')
        new_person.addresses.append(
            Address(email='a@gmail.com', person=new_person))
        new_person.addresses.append(
            Address(email='a@outlook.com', person=new_person))
        db.session.add(new_person)
        db.session.commit()

        test_person = Person.query.filter_by(name='A').one()
        print(test_person)
        print(test_person.addresses.first())
