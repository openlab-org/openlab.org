web: gunicorn config.wsgi:application
worker: celery worker --app=openlab.taskapp --loglevel=info
