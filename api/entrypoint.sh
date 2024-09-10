#!/bin/sh

if [ "$FLASK_ENV" = "production" ]; then
    echo "Running in production mode"
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
else
    echo "Running in development mode"
    exec python -m flask run --host=0.0.0.0 --reload
fi