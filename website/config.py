import os


class Config:
    SECRET_KEY = '2a3bae1c32e2752db72f5a6cd182ca42'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    ELASTICSEARCH_URL = 'http://localhost:9200'
    POSTS_PER_PAGE = 10
    LANGUAGES = ['en', 'es', 'yo']