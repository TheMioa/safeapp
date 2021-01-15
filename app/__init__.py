from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)

if __name__ == "__main__":
    app.run(ssl_context=('cetrs/cert.pem', 'certs/key.pem'))

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import routes, models, errors