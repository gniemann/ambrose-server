from flask import Flask

from .models import db, migrate
from .common import login_manager
from .api import api_bp
from .web import web_bp, tasks_bp


def build_app(config):
    app = Flask('devops_monitor')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp, url_prefix='/web')
    app.register_blueprint(tasks_bp, url_prefix='/web/tasks')

    return app
