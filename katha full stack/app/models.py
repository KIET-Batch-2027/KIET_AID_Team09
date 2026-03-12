from datetime import datetime

from flask_login import UserMixin

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    avatar = db.Column(db.String(255), nullable=True, default='avatars/avatar1.svg')
    preferred_language = db.Column(db.String(10), nullable=False, default='en')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    stories = db.relationship('Story', backref='author', lazy=True, cascade='all, delete-orphan')

    def is_admin(self):
        return self.role == 'admin'


class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    genre = db.Column(db.String(30), nullable=False)
    length = db.Column(db.String(20), nullable=False)
    story_text = db.Column(db.Text, nullable=False)
    audio_file_path = db.Column(db.String(255), nullable=True)
    is_child_safe = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))