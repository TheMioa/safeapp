import base64
from math import log
from flask import render_template
from flask_mail import Message
from app import mail, app
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def entropy(string):
        prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]
        entropy = - sum([ p * log(p) / log(2.0) for p in prob ])

        return entropy

def send_password_reset_email(user):
        token = user.get_reset_password_token()
        t = render_template('email/reset_password.html', user=user, token=token)
        with open("reset_password.txt", "w") as fh:
                fh.write(t)

def generate_fernet_key(password, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=213700)
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))