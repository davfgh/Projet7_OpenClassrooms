#!/bin/bash
source .venv/bin/activate
exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker api.app:app --bind 0.0.0.0:8000
