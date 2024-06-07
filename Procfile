release: python manage.py migrate
web: daphne s_carpool.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker

