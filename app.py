import ambrose
from config import Config

app = ambrose.build_app(Config)
celery = ambrose.make_celery(app)

if __name__ == '__main__':
    app.run()