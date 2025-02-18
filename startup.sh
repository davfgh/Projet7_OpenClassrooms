#!/bin/bash
cd /home/site/wwwroot
source .venv/bin/activate
# gunicorn -w 2 api.app:app --bind 0.0.0.0:8000
export PORT=8000  # Ajout explicite du port
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT
