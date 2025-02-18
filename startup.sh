#!/bin/bash

# cd /home/site/wwwroot

# # ✅ Vérifier que l'environnement virtuel existe
# if [ -d ".venv" ]; then
#     echo "Activation de l'environnement virtuel"
#     source .venv/bin/activate
# else
#     echo "ERREUR : L'environnement virtuel .venv est introuvable"
#     exit 1
# fi

# # 🔹 Vérification et installation des dépendances
# pip install --upgrade pip
# pip install --no-cache-dir -r requirements.txt
# pip install --no-cache-dir numpy gunicorn

# # 🔹 Debugging : Afficher les modules installés
# pip list | grep numpy
# pip list | grep gunicorn

# # ✅ Lancer Gunicorn
# echo "🚀 Lancement de Gunicorn..."
# gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT


cd /home/site/wwwroot

# ✅ Vérifier si l'environnement virtuel existe, sinon le créer
if [ ! -d ".venv" ]; then
    echo ".venv introuvable. Création en cours..."
    python -m venv .venv
fi

echo "✅ Activation de l'environnement virtuel"
source .venv/bin/activate

# 🔹 Vérification et installation des dépendances
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir numpy gunicorn

# 🔹 Debugging : Afficher les modules installés
pip list | grep numpy
pip list | grep gunicorn

# ✅ Lancer Gunicorn
echo "🚀 Lancement de Gunicorn..."
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:$PORT
