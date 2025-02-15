import streamlit as st
import pandas as pd
import numpy as np
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
import requests
import shap
import pickle
import os
import warnings


# 🔧 Configuration des logs
logging.basicConfig(level=logging.DEBUG, format="DEBUG:%(message)s")
warnings.simplefilter("always")  # Activer tous les warnings

# 📂 Définition des chemins
base_dir = "D:/Pro/OpenClassrooms/Projet_7/3_dossier_code_012025"
model_path = os.path.join(base_dir, "models", "lgbm_final_model.pkl")
features_path = os.path.join(base_dir, "features", "app_test_features.csv")

# 🎯 Initialisation des états de session
if "selected_client" not in st.session_state:
    st.session_state.selected_client = None
if "margin" not in st.session_state:
    st.session_state.margin = 0.00  # Par défaut, pas de zone grise

# 📌 1. Chargement du Modèle et des Données
st.header("📌 1. Chargement")
try:
    with open(model_path, "rb") as f:
        model_data = pickle.load(f)
    model = model_data["model"]
    features_names = model_data["features"]
    optimal_threshold = model_data["optimal_threshold"]
    st.success("✅ Modèle chargé avec succès !")

    data = pd.read_csv(features_path)
    st.success("✅ Données chargées avec succès !")

    # ℹ️ Infobulle sur le seuil optimal
    with st.expander("ℹ️ **Explication sur le seuil optimal**"):
        st.write(
            "🔹 Le **seuil optimal** est la probabilité à partir de laquelle un client est "
            "considéré comme **risqué**. Il a été optimisé selon les **critères métier**.\n\n"
            "🔹 Vous pouvez **ajuster la marge** autour de ce seuil pour définir une **zone grise** "
            "(intervalle d'incertitude où le modèle n'est pas certain de la classification)."
        )

    st.write(f"🔹 **Seuil optimal** : {optimal_threshold:.3f}")
    st.write(f"🔹 **Nombre total de clients dans le dataset** : {data.shape[0]}")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des fichiers : {e}")

# 📌 2. Sélection du Client Aléatoire et Comparaison avec la Moyenne
st.header("📌 2. Sélection d'un client")

# 🎲 Bouton pour sélectionner un autre client aléatoire
# if st.button("🎲 Sélectionner un autre client aléatoire"):
#     st.session_state.selected_client = None  # Réinitialiser la sélection

if st.button("🎲 Sélectionner un autre client aléatoire"):
    st.session_state.selected_client = None  # Réinitialiser la sélection
    if "shap_values_data" in st.session_state:
        del st.session_state.shap_values_data  # Supprimer les valeurs SHAP pour forcer la mise à jour

try:
    # 🔎 Filtrer les clients sans valeurs manquantes
    data_clean = data.dropna()

    if data_clean.empty:
        st.warning("⚠️ Aucun client sans valeurs manquantes trouvé.")
    else:
        if "selected_client" not in st.session_state:
            st.session_state.selected_client = None

        if st.session_state.selected_client is None:
            st.session_state.selected_client = data_clean.sample(1, random_state=np.random.randint(1000))

        random_client = st.session_state.selected_client
        client_id = random_client.index[0]

        st.subheader(f"👤 **Client sélectionné (ID : {client_id})**")

        # 📊 **Comparaison aux clients de la même classe**
        st.subheader("📊 **Comparaison aux clients de la même classe**")

        # 📌 Calcul des statistiques pour chaque feature
        mean_std = data_clean[features_names].agg(["mean", "std"])

        # Remplissage du DataFrame
        rows_list = []  # Stocker les lignes avant de créer le DataFrame

        for feature in features_names:
            val_client = random_client[feature].values[0]
            mean_val = mean_std.loc["mean", feature]
            std_val = mean_std.loc["std", feature]
            lower_bound, upper_bound = mean_val - std_val, mean_val + std_val

            if lower_bound <= val_client <= upper_bound:
                statut = "🟩 Dans l'intervalle"
            else:
                statut = "🟥 Hors de l'intervalle"

            # Ajouter une ligne sous forme de dictionnaire
            rows_list.append({
                "Feature": feature,
                "Valeur Client": val_client,
                "Moyenne": mean_val,
                "Écart-Type": std_val,
                "Statut": statut
            })

        # Création du DataFrame final
        comparison_df = pd.DataFrame(rows_list)

        # Affichage
        # st.dataframe(comparison_df, use_container_width=True)
        st.dataframe(
            comparison_df.style.format({"Valeur Client": "{:.3f}", "Moyenne": "{:.3f}", "Écart-Type": "{:.3f}"}),
            use_container_width=True
            )

except Exception as e:
    st.error(f"❌ Erreur lors de la sélection du client : {e}")

# 📌 3. Prédiction et Réglage de la Zone Grise
st.header("📌 3. Prédiction")

try:
    # 📌 Préparation des données pour la prédiction
    input_data = random_client[features_names].to_dict(orient='records')[0]

    # 🔗 URL de l'API
    api_url = "http://127.0.0.1:5000/predict"

    # 🚀 Debugging avant l'appel API
    print(f"🔍 Vérification - Envoi de la requête API avec les données suivantes : {input_data}")
    print(f"🔍 API URL: {api_url}")

    # 🚀 Envoi de la requête à l'API
    response = requests.post(api_url, json=input_data)

    if response.status_code == 200:
        prediction = response.json()

        # 📌 **Gestion de la Zone Grise**
        st.subheader("⚙️ **Réglage du seuil de définition de zone grise (optionnel)**")

        st.session_state.margin = st.slider(
            "Marge de la zone grise (%)", min_value=0.0, max_value=0.10, value=0.00, step=0.01, key="zone_grise_slider"
        )

        # 📌 **Calcul des seuils dynamiques**
        margin_value = st.session_state.margin
        lower_bound = optimal_threshold - margin_value
        upper_bound = optimal_threshold + margin_value
        probability_class_1 = prediction['probability_class_1']

        # ℹ️ Infobulle sur la zone grise
        with st.expander("ℹ️ **Comment fonctionne la zone grise ?**"):
            st.write(
                f"🔹 Si la **probabilité d'appartenir à la classe risquée** se situe entre "
                f"les limites définies par le seuil ± marge, le client sera classé dans une **zone d'incertitude**.\n\n"
                f"🔹 **Intervalle dynamique actuel** : [{lower_bound:.3f}, {upper_bound:.3f}]"
            )

        # 📌 **Calcul des seuils dynamiques**
        margin_value = st.session_state.margin
        lower_bound = optimal_threshold - margin_value
        upper_bound = optimal_threshold + margin_value
        # probability_class_1 = prediction['probability_class_1']
        probability_class_1 = prediction.get('probability_class_1', None)
        if probability_class_1 is None:
            st.error("❌ Erreur : La réponse de l'API ne contient pas la clé 'probability_class_1'. Vérifiez l'API.")

        # 📌 **Détermination du verdict final**
        if probability_class_1 < lower_bound:
            verdict = "Classe_0 (Fiable)"
            verdict_color = "lightgreen"
        elif probability_class_1 > upper_bound:
            verdict = "Classe_1 (Risqué)"
            verdict_color = "#FFCCCB"  # Rouge clair
        else:
            verdict = "Zone Grise (Incertitude)"
            verdict_color = "#FFD700"  # Jaune

        # 📌 **Affichage de la probabilité
        st.markdown(
            f'<div style="background-color: #333333; padding: 10px; border-radius: 10px; '
            f'text-align: center; font-size: 18px; font-weight: bold; color: white; margin-bottom: 20px;">'
            f'📊 **Probabilité d\'être un client risqué** : {probability_class_1:.2%}'
            '</div>',
            unsafe_allow_html=True
        )

        # 📌 **Affichage du Verdict**
        st.markdown(
            f'<div style="background-color: {verdict_color}; padding: 15px; border-radius: 10px;">'
            f'<h3 style="text-align: center; color: black;">🔮 {verdict}</h3>'
            '</div>',
            unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"❌ Erreur lors de la requête à l'API : {e}")

# 📌 4. Feature Importance Locale (SHAP)
st.header("📌 4. Feature Importance Locale")

st.markdown(
    "ℹ️ **Pourquoi cette analyse ?**\n"
    "Cette section montre **les principales variables qui influencent** la prédiction du modèle **pour ce client spécifique**."
)

# ℹ️ Infobulle sur le SHAP Waterfall Plot
with st.expander("ℹ️ **Comment lire ce graphique ?**"):
    st.write(
        "- 🟥 **Facteurs augmentant la probabilité d'être risqué** : Ces features poussent la prédiction vers un risque élevé.\n"
        "- 🟦 **Facteurs réduisant le risque** : Ces features diminuent la probabilité que le client soit risqué."
    )

# 📌 Endpoint de l'API pour récupérer les SHAP values
api_shap_url = "http://127.0.0.1:5000/shap_values"

# 📌 Vérification et récupération des données SHAP avec mise en cache
if "shap_values_data" not in st.session_state:
    try:
        response = requests.get(api_shap_url)

        if response.status_code == 200:
            st.session_state.shap_values_data = response.json()
        else:
            st.error(f"❌ Erreur API SHAP : {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur de connexion à l'API SHAP : {e}")

# 📌 Utilisation des données SHAP en cache si disponibles
if "shap_values_data" in st.session_state:
    shap_data = st.session_state.shap_values_data

    # 🔍 Extraction des données de l'API
    shap_values = np.array(shap_data["shap_values"]).reshape(1, -1)  # Assurer (1, N)
    feature_names = shap_data["features_names"]
    sample_values = np.array(shap_data["sample_values"]).reshape(1, -1)  # Même format (1, N)
    base_values = shap_data["base_values"]

    # 📌 Vérification des dimensions après correction
    print(f"📌 SHAP values shape : {shap_values.shape}")
    print(f"📌 Feature names count : {len(feature_names)}")
    print(f"📌 Sample values shape : {sample_values.shape}")

    # 📌 Création d'un objet SHAP Explanation pour afficher la figure waterfall
    explainer = shap.Explanation(
        values=shap_values[0],  # Prendre la première (et unique) ligne
        base_values=base_values,
        data=sample_values[0],  # Correspondance avec les features
        feature_names=feature_names
    )

    # 📊 Génération et affichage du Waterfall Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.waterfall_plot(explainer, max_display=11, show=False)
    plt.title(f"Impact des principales features sur la prédiction")
    st.pyplot(fig)

    st.markdown("🔍 **Figure : SHAP Waterfall Plot des principales features**")

else:
    st.error("❌ Les données SHAP n'ont pas pu être récupérées.")
