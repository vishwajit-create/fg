import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

        # Automatic IPv4 Pooler conversion for Supabase on IPv6-restricted hosts (like Render)
        if 'db.ckgilqoqprkeutxvzmth.supabase.co' in db_url:
            db_url = db_url.replace('@db.ckgilqoqprkeutxvzmth.supabase.co', '@aws-1-ap-northeast-1.pooler.supabase.com')
            if '://postgres:' in db_url:
                db_url = db_url.replace('://postgres:', '://postgres.ckgilqoqprkeutxvzmth:')

    SQLALCHEMY_DATABASE_URI = db_url or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'csfms.db').replace('\\', '/')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
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
