#!/bin/bash
cd /home/site/wwwroot
source .venv/bin/activate
PORT=${PORT:-8000}
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
