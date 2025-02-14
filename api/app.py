from flask import Flask, request, jsonify
import pickle
import numpy as np
import os
import shap
from pathlib import Path

print("🚀 Démarrage du script Flask...")  # Vérifier si Flask démarre bien

# 📌 Charger le modèle depuis le fichier pickle
# base_dir = os.path.dirname(os.getcwd()) # fonctionne uniquement en local
# base_dir = os.getcwd() # fonctionne uniquement dans les actions git
# file_path = os.path.join(base_dir, "models", "lgbm_final_model.pkl") # fonctionne dans un des deux cas

# Tester si cela fonctionne dans les deux cas
base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "models" / "lgbm_final_model.pkl"

print(f"📂 Chemin du fichier Pickle : {file_path}")

# ✅ Vérifier si le fichier Pickle existe
if not os.path.exists(file_path):
    print(f"❌ Erreur : Le fichier Pickle '{file_path}' est introuvable.")
    exit()

print("📌 Chargement du fichier Pickle...")

try:
    with open(file_path, "rb") as f:
        model_data = pickle.load(f)
    print("✅ Modèle chargé avec succès !")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle : {e}")
    exit()

# 📌 Vérifier le contenu du fichier Pickle
if not isinstance(model_data, dict) or "model" not in model_data or "features" not in model_data:
    print("❌ Erreur : Le fichier Pickle ne contient pas les bonnes clés ('model', 'features').")
    exit()

# 📌 Récupération du modèle et des features
model = model_data["model"]
features_names = model_data["features"]
optimal_threshold = model_data["optimal_threshold"]

print(f"✅ Nombre de features : {len(features_names)}")
print(f"📌 Seuil optimal utilisé pour la classification : {optimal_threshold:.3f}")

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint Flask pour effectuer une prédiction avec le modèle entraîné.
    Intègre une marge autour du seuil optimal.
    """
    try:
        # Récupération des données JSON envoyées
        input_data = request.get_json()

        # Vérifier si toutes les features attendues sont présentes
        missing_features = [feat for feat in features_names if feat not in input_data]
        if missing_features:
            return jsonify({"error": f"Features manquantes : {missing_features}"}), 400

        # Convertir les données en array numpy
        input_array = np.array([list(input_data[feat] for feat in features_names)]).reshape(1, -1)

        # Prédiction avec le modèle
        prediction_proba = model.predict_proba(input_array)[0][1]  # Probabilité d'être en classe 1 (risqué)

        # Définir une marge autour du seuil
        margin = 0
        lower_bound = optimal_threshold - margin
        upper_bound = optimal_threshold + margin

        # Classification avec la marge
        if prediction_proba < lower_bound:
            prediction_class = "Classe_0 (fiable)"
        elif prediction_proba > upper_bound:
            prediction_class = "Classe_1 (risqué)"
        else:
            prediction_class = "Zone grise (incertain)"

        # Construire la réponse
        response = {
            "prediction": prediction_class,
            "probability_class_1": float(prediction_proba),
            "probability_class_0": float(1 - prediction_proba),
            "optimal_threshold": optimal_threshold,
            "margin": margin,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/shap_values', methods=['GET'])
def get_shap_values():
    """
    Endpoint Flask pour récupérer les valeurs SHAP d'un échantillon.
    Permet d'afficher l'explication SHAP dans la démo Streamlit.
    """
    try:
        # Générer un échantillon aléatoire pour l'explication SHAP
        num_samples = 1  # Un seul exemple pour éviter une réponse trop lourde
        sample_data = np.random.randn(num_samples, len(features_names))  # Génération aléatoire (à adapter si dataset disponible)

        # Vérifier si le modèle supporte SHAP
        if "lightgbm" in str(type(model)).lower():
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(sample_data)
            base_values = explainer.expected_value
        else:
            explainer = shap.Explainer(model, sample_data)
            shap_values = explainer(sample_data).values
            base_values = explainer.expected_value

        # Vérifier si SHAP génère une liste (cas binaire)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Sélectionner la classe risquée (1)

        # Construire la réponse JSON
        response = {
            "shap_values": shap_values.tolist(),  # Conversion en liste pour JSON
            "base_values": base_values.tolist() if isinstance(base_values, np.ndarray) else float(base_values),
            "features_names": features_names,
            "sample_values": sample_data.tolist(),
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Lancement de l'API Flask...")
    app.run(host='127.0.0.1', port=5000, debug=True)
