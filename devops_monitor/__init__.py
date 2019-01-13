from flask import Flask

from .models import db, migrate
from .api import api_bp


def build_app(config):
    app = Flask('devops_monitor')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(api_bp, url_prefix='/api')

    return app