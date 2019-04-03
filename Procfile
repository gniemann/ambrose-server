release: flask db upgrade
web: gunicorn app:app
worker: celery worker --concurrency 1 --app=app.celery --loglevel=DEBUG -B