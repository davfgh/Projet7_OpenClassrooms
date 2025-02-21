#!/bin/bash

cd /home/site/wwwroot

if [ ! -d ".venv" ]; then
    echo ".venv introuvable, création en cours..."
    python -m venv .venv
fi

echo "Activation de la venv..."
source .venv/bin/activate

echo "Installation (requirements-prod.txt)..."
pip install --no-cache-dir -r requirements-prod.txt

echo "Vérification de l'installation..."
pip freeze || true

echo "Vérification de l'installation de numpy..."
pip show numpy

echo "🚀 Lancement de Gunicorn..."
# gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:${PORT}
.venv/bin/gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:${PORT}
