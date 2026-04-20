"""ML model definitions, training, and evaluation."""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

ALGORITHM_DESCRIPTIONS: dict[str, str] = {
    "Logistic Regression": (
        "A linear model that uses a logistic function to model binary or multiclass "
        "classification. Fast, interpretable, and works well when classes are linearly separable."
    ),
    "SVM": (
        "Support Vector Machine finds the optimal hyperplane that maximizes the margin "
        "between classes. Effective in high-dimensional spaces and with kernel tricks."
    ),
    "Naive Bayes": (
        "A probabilistic classifier based on Bayes' theorem with the assumption of "
        "feature independence. Very fast and works well with small datasets."
    ),
    "Random Forest": (
        "An ensemble of decision trees that reduces overfitting by averaging predictions. "
        "Robust, handles non-linear relationships, and provides feature importance."
    ),
    "XGBoost": (
        "Extreme Gradient Boosting builds trees sequentially, each correcting the errors "
        "of the previous. Often achieves state-of-the-art results on tabular data."
    ),
    "KNN": (
        "K-Nearest Neighbors classifies a sample based on the majority vote of its k "
        "nearest neighbors. Simple, non-parametric, but sensitive to feature scaling."
    ),
    "Decision Tree": (
        "A tree-structured model that splits data based on feature thresholds. "
        "Highly interpretable but prone to overfitting without depth constraints."
    ),
}


def get_hyperparameter_specs() -> dict[str, list[dict[str, Any]]]:
    """Return widget specifications for each algorithm's hyperparameters."""
    return {
        "Logistic Regression": [
            {"param": "C", "type": "slider", "min": 0.01, "max": 100.0, "default": 1.0, "step": 0.01, "format": "%.2f"},
            {"param": "max_iter", "type": "slider", "min": 100, "max": 1000, "default": 200, "step": 50},
            {"param": "solver", "type": "selectbox", "options": ["lbfgs", "liblinear", "saga"], "default": "lbfgs"},
        ],
        "SVM": [
            {"param": "C", "type": "slider", "min": 0.01, "max": 100.0, "default": 1.0, "step": 0.01, "format": "%.2f"},
            {"param": "kernel", "type": "selectbox", "options": ["rbf", "linear", "poly"], "default": "rbf"},
            {"param": "gamma", "type": "selectbox", "options": ["scale", "auto"], "default": "scale"},
        ],
        "Naive Bayes": [
            {"param": "var_smoothing", "type": "select_slider", "options_expr": "logspace", "min": -12, "max": -6, "default": -9},
        ],
        "Random Forest": [
            {"param": "n_estimators", "type": "slider", "min": 10, "max": 500, "default": 100, "step": 10},
            {"param": "max_depth", "type": "slider", "min": 2, "max": 50, "default": 10, "step": 1, "allow_none": True},
            {"param": "min_samples_split", "type": "slider", "min": 2, "max": 20, "default": 2, "step": 1},
        ],
        "XGBoost": [
            {"param": "n_estimators", "type": "slider", "min": 50, "max": 500, "default": 100, "step": 10},
            {"param": "max_depth", "type": "slider", "min": 2, "max": 15, "default": 6, "step": 1},
            {"param": "learning_rate", "type": "slider", "min": 0.01, "max": 0.5, "default": 0.1, "step": 0.01, "format": "%.2f"},
        ],
        "KNN": [
            {"param": "n_neighbors", "type": "slider", "min": 1, "max": 50, "default": 5, "step": 1},
            {"param": "weights", "type": "selectbox", "options": ["uniform", "distance"], "default": "uniform"},
        ],
        "Decision Tree": [
            {"param": "max_depth", "type": "slider", "min": 2, "max": 50, "default": 10, "step": 1, "allow_none": True},
            {"param": "min_samples_split", "type": "slider", "min": 2, "max": 20, "default": 2, "step": 1},
            {"param": "criterion", "type": "selectbox", "options": ["gini", "entropy"], "default": "gini"},
        ],
    }


def build_model(algo_name: str, params: dict[str, Any], n_classes: int = 2) -> BaseEstimator:
    """Instantiate a classifier with the given hyperparameters."""
    if algo_name == "Logistic Regression":
        return LogisticRegression(**params, random_state=42)
    if algo_name == "SVM":
        return SVC(**params, probability=True, random_state=42)
    if algo_name == "Naive Bayes":
        return GaussianNB(**params)
    if algo_name == "Random Forest":
        return RandomForestClassifier(**params, random_state=42, n_jobs=-1)
    if algo_name == "XGBoost":
        xgb_params = {**params, "random_state": 42, "use_label_encoder": False, "verbosity": 0}
        if n_classes > 2:
            xgb_params["objective"] = "multi:softprob"
            xgb_params["num_class"] = n_classes
        return XGBClassifier(**xgb_params)
    if algo_name == "KNN":
        return KNeighborsClassifier(**params, n_jobs=-1)
    if algo_name == "Decision Tree":
        return DecisionTreeClassifier(**params, random_state=42)
    raise ValueError(f"Unknown algorithm: {algo_name}")


def train_model(
    model: BaseEstimator,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> tuple[BaseEstimator, float]:
    """Fit a model and return (fitted_model, training_time_seconds)."""
    start = time.perf_counter()
    model.fit(X_train, y_train)
    elapsed = time.perf_counter() - start
    return model, elapsed


def evaluate_model(
    model: BaseEstimator,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    """Compute classification metrics for a trained model."""
    y_pred = model.predict(X_test)
    is_binary = len(class_names) == 2

    metrics: dict[str, Any] = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision (macro)": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "Precision (weighted)": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "Recall (macro)": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "Recall (weighted)": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "F1 (macro)": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "F1 (weighted)": f1_score(y_test, y_pred, average="weighted", zero_division=0),
    }

    # ROC-AUC
    try:
        y_proba = model.predict_proba(X_test)
        if is_binary:
            metrics["ROC-AUC"] = roc_auc_score(y_test, y_proba[:, 1])
        else:
            metrics["ROC-AUC"] = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
    except Exception:
        metrics["ROC-AUC"] = None

    metrics["y_pred"] = y_pred
    try:
        metrics["y_proba"] = model.predict_proba(X_test)
    except Exception:
        metrics["y_proba"] = None

    return metrics


def get_feature_importance(
    model: BaseEstimator,
    feature_names: list[str],
) -> pd.DataFrame | None:
    """Extract feature importances or coefficients from a model."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = model.coef_
        if coef.ndim > 1:
            importances = np.mean(np.abs(coef), axis=0)
        else:
            importances = np.abs(coef.ravel())
    else:
        return None

    if len(importances) != len(feature_names):
        return None

    df = pd.DataFrame({"feature": feature_names, "importance": importances})
    return df.sort_values("importance", ascending=False).reset_index(drop=True)


def get_classification_report_df(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
) -> pd.DataFrame:
    """Return sklearn classification report as a clean DataFrame."""
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    df = pd.DataFrame(report).T
    df = df.round(4)
    return df
