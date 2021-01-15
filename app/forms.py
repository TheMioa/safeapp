from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User, Post
from app.utils import entropy

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Hasło ma mieć conajmniej 8 znaków')])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Podany użytkownik już istnieje')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Podany adres email jest już w użyciu')
    
    def validate_password(self, password):
        ent = entropy(password.data)
        if ent <= 3.0:
            raise ValidationError('Hasło za słabe, podaj mocniejsze')


class PostForm(FlaskForm):
    post = TextAreaField('Treść notatki', validators=[DataRequired(), Length(max=255, message='Notatka może mieć max 255 znaków')])
    priv_recipient = StringField('Prywatny odbiorca')
    public = BooleanField('Publiczny', default=False)
    submit = SubmitField('Submit')

    def validate_public(self, public):
        if public.data == True:
            if self.priv_recipient.data != '':
                raise ValidationError('Wiadomość prywatna nie może być publiczna')
    
    def validate_priv_recipient(self, priv_recipient):
        if priv_recipient.data != '':
            user = User.query.filter_by(username=priv_recipient.data).first()
            if user is None:
                raise ValidationError('Podany użytkownik nie istnieje') 

class FileForm(FlaskForm):
    file = FileField('File', validators=[FileRequired(message='Plik nie moze być pusty'), FileAllowed(upload_set = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], message='Niedozwolony format pliku!')])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Password Reset')

class EncryptedNotesForm(FlaskForm):
    post = TextAreaField('Treść notatki', validators=[DataRequired(), Length(max=255, message='Notatka może mieć max 255 znaków')])
    password = PasswordField('Hasło notatki', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DecrypytNotesForm(FlaskForm):
    note_id = StringField('Numer notatki', validators=[DataRequired(), Length(min=36, max=36, message='Unikalny numer notatki ma dokładnie 36 znaków')])
    password = PasswordField('Hasło notatki', validators=[DataRequired()])
    submit = SubmitField('Submit')