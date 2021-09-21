web: gunicorn project.wsgi
release: django-admin migrate --noinput --fake
worker: django-admin rqworker default
