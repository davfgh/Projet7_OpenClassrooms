#!/bin/bash

# cd /home/site/wwwroot

# # ✅ Vérifier que Python est bien installé
# echo "📌 Python version : $(python --version)"
# echo "📌 Gunicorn version : $(gunicorn --version)"

# # ✅ Vérifier si l'environnement virtuel existe, sinon le créer
# if [ ! -d "/home/site/wwwroot/.venv" ]; then
#     echo "❌ .venv introuvable, création en cours..."
#     python -m venv /home/site/wwwroot/.venv
#     echo "✅ .venv créé !"
# fi

# # ✅ Activer le venv
# echo "📌 Activation de l'environnement virtuel..."
# source /home/site/wwwroot/.venv/bin/activate
# echo "✅ Environnement activé."

# # 🔹 Installation des dépendances
# pip install --upgrade pip
# pip install --no-cache-dir -r requirements.txt
# pip install --no-cache-dir numpy gunicorn

# # ✅ Lancer Gunicorn
# echo "🚀 Lancement de Gunicorn..."
# gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:${PORT}
# echo "🔍 PORT utilisé : $PORT"

# # Vérification des contenu des dossiers
# echo "📌 Contenu du dossier courant :"
# ls -la
# echo "📌 Contenu du dossier API :"
# ls -la api


cd /home/site/wwwroot

# ✅ Vérifier si le dossier .venv existe
if [ ! -d ".venv" ]; then
    echo "❌ .venv introuvable, création en cours..."
    python -m venv .venv
    # Activer immédiatement pour l'install
    source .venv/bin/activate
    echo "✅ .venv créé !"
else
    echo "✅ .venv déjà présent, activation..."
    source .venv/bin/activate
fi

# 🔹 Installation des dépendances
echo "📌 Mise à jour pip + install requirements..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir numpy gunicorn

echo "🚀 Lancement de Gunicorn..."
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:${PORT}
