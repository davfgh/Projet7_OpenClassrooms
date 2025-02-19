#!/bin/bash

# cd /home/site/wwwroot

# # ✅ Vérifier que l'environnement virtuel existe, sinon le créer
# if [ ! -d ".venv" ]; then
#     echo "❌ .venv introuvable, création en cours..."
#     python -m venv .venv
#     source .venv/bin/activate
#     echo "✅ Environnement virtuel créé et activé."
# else
#     echo "✅ Activation de l'environnement virtuel existant."
#     source .venv/bin/activate
# fi

# # 🔹 Installation des dépendances
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

# ✅ Vérifier si Python est bien installé
echo "📌 Version de Python utilisée :"
python --version

# ✅ Vérifier si l'environnement virtuel existe, sinon le créer
if [ ! -d "/home/site/wwwroot/.venv" ]; then
    echo "❌ .venv introuvable, création en cours..."
    python -m venv /home/site/wwwroot/.venv
    echo "✅ .venv créé !"
fi

# ✅ Activer le venv
echo "📌 Activation de l'environnement virtuel..."
source /home/site/wwwroot/.venv/bin/activate
echo "✅ Environnement activé."

# 🔹 Installation des dépendances
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir numpy gunicorn

# 🔹 Debugging : Afficher les modules installés
pip list | grep numpy
pip list | grep gunicorn

# ✅ Lancer Gunicorn (forcer le port avec $PORT)
echo "🚀 Lancement de Gunicorn..."
gunicorn -w 2 --chdir api app:app --bind 0.0.0.0:${PORT}
