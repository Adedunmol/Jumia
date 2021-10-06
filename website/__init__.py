from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from website.config import Config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    from .auth import auth
    from .views import views
    from .handlers import errors

    app.register_blueprint(auth)
    app.register_blueprint(views)
    app.register_blueprint(errors)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    from .models import User, Post

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + 'site.db'):
        db.create_all(app=app)
        print('Created Database!')
