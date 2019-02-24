from flask import Flask
from flask_jwt_extended import JWTManager

from .models import db, migrate
from .common import login_manager
from .api import api_bp
from .web import web_bp, tasks_bp, accounts_bp, messages_bp

jwt = JWTManager()

def build_app(config):
    app = Flask('devops_monitor')
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

    return app
