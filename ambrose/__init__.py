import celery
from flask import Flask

from ambrose.web.devices import devices_bp
from .models import db, migrate
from .common import login_manager
from .api import api_bp
from .web import web_bp, tasks_bp, accounts_bp, messages_bp, gauges_bp
from .tasks import celery_app
from .services import jwt

def make_celery(app):
    celery_app.conf.update(BROKER_URL=app.config['CELERY_BROKER_URL'])

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask
    return celery_app

def build_app(config):
    app = Flask('ambrose')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp, url_prefix='/web')
    app.register_blueprint(tasks_bp, url_prefix='/web/tasks')
    app.register_blueprint(accounts_bp, url_prefix='/web/accounts')
    app.register_blueprint(messages_bp, url_prefix='/web/messages')
    app.register_blueprint(gauges_bp, url_prefix='/web/gauges')
    app.register_blueprint(devices_bp, url_prefix='/web/devices')

    return app
