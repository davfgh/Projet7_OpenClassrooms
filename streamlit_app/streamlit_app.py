import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import shap
import pickle
import os
import warnings
import logging

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
if st.button("🎲 Sélectionner un autre client aléatoire"):
    st.session_state.selected_client = None  # Réinitialiser la sélection

try:
    # 🔎 Filtrer les clients sans valeurs manquantes
    data_clean = data.dropna()

    if data_clean.empty:
        st.warning("⚠️ Aucun client sans valeurs manquantes trouvé.")
    else:
        # 🎯 Sélectionner un client aléatoire si aucun n'est déjà sélectionné
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

    # 🚀 Envoi de la requête à l'API
    response = requests.post(api_url, json=input_data)

    if response.status_code == 200:
        prediction = response.json()

        # 📌 **Gestion de la Zone Grise**
        st.subheader("⚙️ **Réglage du seuil de définition de zone grise (optionnel)**")

        st.session_state.margin = st.slider(
            "Marge de la zone grise (%)", min_value=0.0, max_value=0.10, value=0.00, step=0.01
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
        probability_class_1 = prediction['probability_class_1']

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

try:
    explainer = shap.Explainer(model)
    shap_values = explainer(random_client[features_names])

    fig, ax = plt.subplots(figsize=(10, 8))
    shap.waterfall_plot(shap_values[0], max_display=10, show=False)
    plt.title(f"Impact des principales features sur la prédiction (Client {client_id})")
    st.pyplot(fig)

    st.markdown("🔍 **Figure : SHAP Waterfall Plot des 10 principales features**")

except Exception as e:
    st.error(f"❌ Erreur lors de la génération de la Feature Importance Locale : {e}")
