#!/bin/bash

cd /home/site/wwwroot

# ✅ Vérifier que l'environnement virtuel existe, sinon le créer
if [ ! -d ".venv" ]; then
    echo "❌ .venv introuvable, création en cours..."
    python -m venv .venv
    source .venv/bin/activate
    echo "✅ Environnement virtuel créé et activé."
else
    echo "✅ Activation de l'environnement virtuel existant."
    source .venv/bin/activate
fi

# 🔹 Installation des dépendances
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir numpy gunicorn

# 🔹 Debugging : Afficher les modules installés
pip list | grep numpy
pip list | grep gunicorn

# ✅ Lancer Gunicorn
echo "🚀 Lancement de Gunicorn..."
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT
