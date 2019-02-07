from flask import Flask

from .models import db, migrate
from .api import api_bp
from .web import web_bp, login_manager


def build_app(config):
    app = Flask('devops_monitor')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp, url_prefix='/web')

    return app
