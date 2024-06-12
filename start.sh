#!/bin/sh

# Activate Python virtual environment
source .venv/bin/activate

# Start Uvicorn
exec gunicorn --reload config.wsgi:application --bind 0.0.0.0:8000