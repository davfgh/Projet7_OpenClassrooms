#!/bin/bash
cd /home/site/wwwroot
source .venv/bin/activate
gunicorn -w 2 api.app:app --bind 0.0.0.0:8000
