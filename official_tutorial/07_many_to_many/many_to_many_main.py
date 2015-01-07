from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))
    tags = db.relationship(lambda: Tag, secondary=lambda: tags, backref=db.backref('pages', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return "<Page {0}>".format(self.text)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    def __repr__(self):
        return "<Tag {0}>".format(self.name)


tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey(Tag.id)),
    db.Column('page_id', db.Integer, db.ForeignKey(Page.id)))


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
        python_tag = Tag(name='python')
        server_tag = Tag(name='server')
        client_tag = Tag(name='client')
        db.session.add(Page(text='flask', tags=[python_tag, server_tag]))
        db.session.add(Page(text='django', tags=[python_tag, server_tag]))
        db.session.add(Page(text='kivy', tags=[python_tag, client_tag]))
        db.session.commit()

        page = Page.query.filter_by(text='flask').one()
        print(page.tags.all())

        tag = Tag.query.filter_by(name='client').one()
        print(tag.pages.all())
