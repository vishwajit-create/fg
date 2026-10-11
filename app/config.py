import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'csfms.db').replace('\\', '/')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    INSTITUTION_NAME = os.environ.get('INSTITUTION_NAME', 'College Student & Faculty Management System')
    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Kolkata')
    ROWS_PER_PAGE = 20
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    WTF_CSRF_SSL_STRICT = True
    SESSION_COOKIE_SECURE = True



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
