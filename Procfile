release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT s_carpool.asgi:application
worker: python manage.py runworker

