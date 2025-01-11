import pytest
from lightgbm import LGBMClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

@pytest.fixture
def data():
    """
    Génère un dataset fictif pour les tests unitaires.

    Cette fonction utilise `make_classification` de scikit-learn pour créer un dataset
    de classification avec 1000 échantillons et 10 caractéristiques. Les données sont
    ensuite divisées en ensembles d'entraînement et de test à l'aide de
    `train_test_split`.

    Returns:
        tuple: Un tuple contenant les ensembles (X_train, X_test, y_train, y_test).
    """
    # Génère un dataset fictif
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    return train_test_split(X, y, random_state=42)

def test_training(data):
    """
    Teste l'entraînement et l'évaluation d'un modèle LightGBM.

    Ce test entraîne un modèle LightGBM sur un dataset fictif et vérifie que
    le score AUC (Area Under Curve) est supérieur à un seuil de 0.7. Si l'AUC est
    inférieur à ce seuil, le test échoue.

    Args:
        data (tuple): Un tuple contenant les ensembles (X_train, X_test, y_train, y_test),
                      généré par la fixture `data()`.

    Raises:
        AssertionError: Si le score AUC est inférieur à 0.7.
    """
    # Teste que le modèle peut être entraîné et donne une AUC acceptable
    X_train, X_test, y_train, y_test = data

    # Entraîne le modèle
    model = LGBMClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Évalue le modèle
    auc_score = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    # Vérifie que l'AUC est supérieur à 0.7
    assert auc_score > 0.7, f"AUC trop faible : {auc_score}"
