Documentation de l'API de Scoring Client

1. Introduction

Cette API permet d'effectuer des prédictions sur la fiabilité d'un client en fonction de ses caractéristiques. Elle utilise un modèle de machine learning sérialisé via pickle et propose un point d'entrée pour soumettre des requêtes et obtenir un score de risque.

2. Architecture

L'API est développée avec Flask et fonctionne comme suit :

Chargement du modèle stocké dans un fichier pickle.

Vérification des données d'entrée.

Prédiction du risque client via le modèle.

Retour des résultats sous forme de réponse JSON.

L'API est utilisée à la fois par une application Streamlit et un notebook de test.

3. Installation et Exécution

3.1 Prérequis

Avant de démarrer l'API, assurez-vous d'avoir installé les dépendances nécessaires :

pip install -r requirements.txt

3.2 Lancement de l'API

L'API se lance via le fichier app.py :

python app.py

Elle s'exécutera sur http://127.0.0.1:5000/.

4. Endpoints

4.1 Endpoint de prédiction

URL : /predict

Méthode : POST

Description : Prend en entrée un dictionnaire JSON contenant les caractéristiques d'un client et retourne la prédiction du modèle.

4.1.1 Exemples de requêtes

Requête JSON

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
    "DEBT_CREDIT_RATIO": 0.3,
    "ANNUITY_BIRTH_RATIO": 0.02,
    "ANNUITY_INCOME_PERCENT": 0.1,
    "CREDIT_GOODS_RATIO": 1.1,
    "INSTA_AMT_PAYMENT": 10000,
    "INSTA_NUM_INSTALMENT_VERSION": 3,
    "POS_CNT_INSTALMENT_FUTURE": 2
}

Réponse JSON

{
    "prediction": "Classe_0 (fiable)",
    "probability_class_1": 0.120,
    "probability_class_0": 0.880,
    "optimal_threshold": 0.150,
    "margin": 0.000,
    "lower_bound": 0.150,
    "upper_bound": 0.150
}

5. Gestion des erreurs

L'API intègre plusieurs mécanismes de gestion des erreurs pour assurer une réponse claire en cas de problème.

5.1 Erreurs liées au chargement du modèle

Erreur

Message renvoyé

Modèle introuvable

{ "error": "Le fichier Pickle 'lgbm_final_model.pkl' est introuvable." }

Modèle mal formaté

{ "error": "Le fichier Pickle ne contient pas les bonnes clés ('model', 'features')." }

Erreur lors du chargement

{ "error": "Erreur lors du chargement du modèle : <détails de l'erreur>" }

5.2 Erreurs liées aux données d'entrée

Erreur

Message renvoyé

Features manquantes

{ "error": "Features manquantes : ['nom_feature_manquante']" }

Format incorrect

{ "error": "Erreur lors du traitement des données : <détails de l'erreur>" }

5.3 Erreurs générales

Erreur

Message renvoyé

Erreur interne

{ "error": "<détails de l'erreur>" }

API inaccessible

L'API ne répond pas et retourne un code HTTP 500 ou 503.

6. Structure des fichiers

L'API est organisée comme suit :

api/
│── app.py                 # Script principal de l'API Flask
│── test_api.ipynb         # Notebook de test de l'API
models/
│── lgbm_final_model.pkl   # Modèle de machine learning sérialisé

7. Tests

7.1 Test via le Notebook

Le fichier test_api.ipynb permet de tester l'API localement. Il génère des données aléatoires respectant le format requis, effectue une requête à l'API et affiche les résultats.

Fin de la documentation.
