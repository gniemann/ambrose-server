import celery

celery_app = celery.Celery()

@celery_app.task
def test():
    print("Hello, world!")

