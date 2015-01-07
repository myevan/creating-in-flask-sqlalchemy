from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '<Category {0}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = db.relationship(Category, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<Post {0}>'.format(self.title)

db.create_all()

new_category = Category(name="Python")
new_post = Post(title="Hello Python!", body='Python is pretty cool', category=new_category)
db.session.add(new_category)
db.session.add(new_post)

for post in new_category.posts:
    print(post)

print(new_category.posts.all())