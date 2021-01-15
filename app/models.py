import jwt
import time as time1
from time import time
from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    priv_message = db.relationship('PrivPost', backref='recipient', lazy='dynamic')
    files = db.relationship('File', backref='owner', lazy='dynamic')
    def check_password(self, password):
        time1.sleep(3)
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User {}>'.format(self.username)  

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    priv_recipient = db.Column(db.String)
    public = db.Column(db.Boolean)
    recipient = db.relationship('PrivPost', backref='priv_post', lazy='dynamic')
    def __repr__(self):
        return '<Post {}>'.format(self.body)

class PrivPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(140))  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uuid = db.Column(db.String(36))

class EncryptedNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(16))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    def check_password(self, password):
        time1.sleep(3)
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    


@login.user_loader
def load_user(id):
    return User.query.get(int(id))