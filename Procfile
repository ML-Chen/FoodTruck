web: gunicorn FoodTruck.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: celery worker --workdir backend --app=FoodTruck --loglevel=info
