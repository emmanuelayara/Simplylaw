from datetime import datetime
from app import db
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(100), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_user_email'),
    )



class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='article', lazy=True)
    likes = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    views = db.Column(db.Integer, default=0)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    cover_image = db.Column(db.String(100))  # New field
    document_filename = db.Column(db.String(120), nullable=True)
    category = db.Column(db.String(100), nullable=False, default='General')
    approved = db.Column(db.Boolean, default=False)  # <- important!


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # Add this
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
