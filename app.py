import devops_monitor
from config import Config

app = devops_monitor.build_app(Config)

if __name__ == '__main__':
    app.run()