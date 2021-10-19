from flask import Flask, request
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from website.config import Config
from elasticsearch import Elasticsearch
from flask_babel import Babel
from flask_babel import lazy_gettext as _l


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = _l('Please log in to access this page.')
bcrypt = Bcrypt()
mail = Mail()
babel = Babel()

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) if app.config['ELASTICSEARCH_URL'] else None


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
    babel.init_app(app)

    from .models import User, Post

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + 'site.db'):
        db.create_all(app=app)
        print('Created Database!')
