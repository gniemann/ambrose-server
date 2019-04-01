import devops_monitor
from config import Config

app = devops_monitor.build_app(Config)
celery = devops_monitor.make_celery(app)

if __name__ == '__main__':
    app.run()