# Documentation de l'API et de l'Interface Streamlit pour le Scoring Client

## 1️. Introduction

Cette web application permet d'effectuer des **prédictions sur la fiabilité d'un client** en fonction de ses caractéristiques financières.

Elle repose sur **deux composants principaux** :
- **Une API Flask**, exposant un modèle de machine learning, permettant d'obtenir un score de risque et des valeurs explicatives via SHAP.
- **Une interface utilisateur Streamlit**, permettant d’explorer les prédictions et d’interagir avec le modèle de manière intuitive.

L'API peut être utilisée **en local** ou **via le déploiement sur le cloud**.

---

## 2️. **Architecture**

### API Flask
- Chargement du modèle stocké dans un fichier pickle.
- Vérification des données d'entrée.
- Prédiction du risque client via le modèle.
- Retour des résultats sous forme de réponse JSON.

### Interface Streamlit
- Affichage des **informations client**.
- Comparaison des caractéristiques avec des moyennes globales.
- Génération d’une **prédiction et ajustement d’un seuil dynamique**.
- Visualisation des **valeurs SHAP locales** pour comprendre l'impact des variables sur la décision.

---

## 3️. **Installation et Exécution**

### **3.1 Prérequis**
Avant de démarrer l’API et Streamlit en local, assurez-vous d’avoir installé les dépendances nécessaires :
```bash
pip install -r requirements.txt
```

### **3.2 Lancement de l’API en local**
Si l’API est déjà en cours d’exécution, il faut d’abord la stopper avant de la relancer :
```bash
taskkill /F /IM python.exe
```

Ensuite, exécutez les commandes suivantes pour démarrer l'API :
```bash
cd api
python app.py
```

Elle s’exécutera sur `http://127.0.0.1:5000/`.

**Note** : Cette étape n'est pas nécessaire pour la version déployée sur le web.

### **3.3 Lancement de l'Interface Streamlit en local**
Après avoir démarré l’API, lancez Streamlit avec la commande suivante :
```bash
cd streamlit_app
streamlit run streamlit_app.py
```

Par défaut, Streamlit sera accessible à l'adresse suivante :
- **Sur la machine locale** : `http://localhost:8501`
- **Sur le réseau local (si configuré)** : `http://<IP_LOCAL>:8501`

---

## 4️. **Déploiement Automatique sur le Cloud**
L’API est déployée sur **Azure** et accessible à l'adresse suivante :
**https://prediction-api.azurewebsites.net**

**Déploiement automatique**
Ce projet utilise le centre de déploiement Azure, assurant un **déploiement continu**.
Le fichier `.github/workflows/api-deployment_prediction.yml` est issu du déploiement automatique généré par Azure.
Une étape supplémentaire a été ajoutée dans la section `build` pour exécuter les **tests unitaires** avant le déploiement.

**Durée du processus** : Le déploiement peut prendre jusqu'à **30 minutes**.

---

## 5️. **Endpoints de l’API**

### **5.1 Endpoint de prédiction (`/predict`)**
- **URL en local** : `http://127.0.0.1:5000/predict`
- **URL après déploiement** : `https://prediction-api.azurewebsites.net/predict`
- **Méthode** : `POST`
- **Description** : Prend en entrée un dictionnaire JSON contenant les caractéristiques d'un client et retourne la prédiction du modèle.

#### **Exemple de requête**
```json
{
    "AMT_ANNUITY": 15000,
    "AMT_CREDIT": 200000,
    "AMT_GOODS_PRICE": 180000,
    "CREDIT_TERM": 60,
    "DAYS_BIRTH": -12000,
    "DAYS_ID_PUBLISH": -3000,
    "DAYS_REGISTRATION": -4000,
    "EXT_SOURCE_1": 0.5,
    "EXT_SOURCE_2": 0.7,
    "EXT_SOURCE_3": 0.6,
    "DEBT_CREDIT_RATIO": 0.3
}
```

#### **Exemple de réponse**
```json
{
    "prediction": "Classe_0 (fiable)",
    "probability_class_1": 0.120,
    "probability_class_0": 0.880,
    "optimal_threshold": 0.150,
    "margin": 0.000,
    "lower_bound": 0.150,
    "upper_bound": 0.150
}
```

### **5.2 Endpoint des valeurs SHAP (`/shap_values`)**
- **URL en local** : `http://127.0.0.1:5000/shap_values`
- **URL après déploiement** : `https://prediction-api.azurewebsites.net/shap_values`
- **Méthode** : `GET`
- **Description** : Retourne les valeurs SHAP pour expliquer la décision du modèle sur un client donné.

#### **Exemple de réponse**
```json
{
    "shap_values": [-0.05, 0.02, -0.01, 0.08],
    "features_names": ["AMT_ANNUITY", "AMT_CREDIT", "AMT_GOODS_PRICE", "DAYS_BIRTH"],
    "sample_values": [15000, 200000, 180000, -12000],
    "base_values": 0.6
}
```

---

## 6️. **Fichier OpenAPI pour tests sur Postman**
Le fichier `openapi.yml` situé dans le dossier `api/` permet de tester facilement les endpoints via **Postman** ou **Swagger UI**.

---

## 7️. **Tests de l'API**
Les **tests unitaires** sont exécutés automatiquement lors du **déploiement sur Azure**.
Ils permettent de s'assurer que les endpoints `/predict` et `/shap_values` fonctionnent correctement.

Pour tester l'API à la fois en local et après déploiement, vous pouvez utiliser le notebook :
📂 `api/Farizon_David_5_notebook_test_API_0125.ipynb`

---

## 8️. **Structure des fichiers**
```bash
📂 projet-scoring-client
│── 📂 api
│   │── app.py                # Script principal de l'API Flask
│   │── Farizon_David_5_notebook_test_API_0125.ipynb  # Notebook pour tester l'API
│   │── openapi.yml            # Spécification OpenAPI pour Postman
│── 📂 models
│   │── lgbm_final_model.pkl  # Modèle ML
│── 📂 features
│   │── app_test_features.csv # Données de test
│── 📂 streamlit
│   │── streamlit_app.py      # Interface utilisateur
│── requirements.txt          # Dépendances
│── README.md                 # Documentation
│── .github/workflows/api-deployment_prediction.yml  # CI/CD
```

**Bonne utilisation de l’API et de l’interface Streamlit !**
