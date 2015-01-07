from flask import Flask
from flask import current_app
from flask_ext_sqlalchemy_sharding import ShardedSQLAlchemy
from random import randrange

db = ShardedSQLAlchemy()

GLOBAL_DB_BIND_KEY = 'global_db'
USER_DB_BIND_KEYS = ['user_db_1', 'user_db_2']


class Device(db.Model):
    __bind_key__ = GLOBAL_DB_BIND_KEY

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guid = db.Column(db.String(32), unique=True)

    @classmethod
    def create_device(cls, *args, **kwargs):
        return cls(*args, **kwargs)


class User(db.Model):
    __bind_key__ = USER_DB_BIND_KEYS

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User {0}>'.format(self.username)

    @classmethod
    def create_user_with_device(cls, device, *args, **kwargs):
        new_user = cls(*args, **kwargs)
        new_user.id = (device.id << 8) | randrange(0, current_app.config['SQLALCHEMY_SHARD_MASK'] + 1)
        return new_user

    @property
    def shard_id(self):
        return self.id & 1


def create_app():
    import os

    app = Flask(__name__)
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_SHARD_SHIFT'] = (8 - len(USER_DB_BIND_KEYS))
    app.config['SQLALCHEMY_SHARD_MASK'] = (1 << 8) - 1
    app.config['SQLALCHEMY_BINDS'] = {
        'global_db': 'sqlite:///temp/global_db.sq3',
        'user_db_1': 'sqlite:///temp/user_db_1.sq3',
        'user_db_2': 'sqlite:///temp/user_db_2.sq3',
    }

    if not os.access('temp', os.R_OK):
        os.makedirs('temp')

    db.init_app(app)
    db.drop_all(app=app)
    db.create_all(app=app)
    return app


def transaction(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except:
            db.session.rollback()
            raise

        db.session.commit()
        return result
    return wrapper


@transaction
def make_user(guid, username, email):
    new_device = Device.create_device(guid=guid)
    db.session.add(new_device)
    db.session.flush()

    new_user = User.create_user_with_device(new_device, username=username, email=email)
    with db.session.sharding(new_user.id):
        db.session.add(new_user)
        db.session.flush()

    return new_user.id

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        a_user_id = make_user('A', 'a', 'a@example.com')
        b_user_id = make_user('B', 'a', 'b@example.com')
        c_user_id = make_user('C', 'c', 'c@example.com')

        with db.session.sharding(a_user_id):
            for user in User.query.all():
                print user

