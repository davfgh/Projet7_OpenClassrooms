#!/bin/bash
cd /home/site/wwwroot
source .venv/bin/activate

# 🔹 Exporter le port
export PORT=8000

# 🔹 Forcer la réinstallation des dépendances
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir numpy gunicorn

# 🔹 Vérification des installations (utile pour le debug)
pip list | grep numpy
pip list | grep gunicorn

# 🔹 Lancer Gunicorn
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT

# cd /home/site/wwwroot
# source .venv/bin/activate
# export PORT=8000
# gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT
