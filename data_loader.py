"""Dataset loading, preprocessing, and splitting utilities."""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

BUILTIN_DATASETS = ["Iris", "Breast Cancer", "Wine", "Titanic"]


@st.cache_data
def load_builtin_dataset(name: str) -> tuple[pd.DataFrame, str]:
    """Load a built-in dataset and return (DataFrame, target_column_name)."""
    if name == "Iris":
        data = load_iris(as_frame=True)
        df = data.frame
        return df, "target"

    if name == "Breast Cancer":
        data = load_breast_cancer(as_frame=True)
        df = data.frame
        return df, "target"

    if name == "Wine":
        data = load_wine(as_frame=True)
        df = data.frame
        return df, "target"

    if name == "Titanic":
        csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "titanic.csv")
        df = pd.read_csv(csv_path)
        df = df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin"], errors="ignore")
        df["Age"] = df["Age"].fillna(df["Age"].median())
        df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])
        df["Fare"] = df["Fare"].fillna(df["Fare"].median())
        return df, "Survived"

    raise ValueError(f"Unknown dataset: {name}")


def load_uploaded_csv(file: Any) -> pd.DataFrame:
    """Read an uploaded CSV file into a DataFrame."""
    try:
        df = pd.read_csv(file)
        if df.empty:
            raise ValueError("The uploaded file is empty.")
        return df
    except pd.errors.ParserError as e:
        raise ValueError(f"Could not parse CSV: {e}") from e


def get_dataset_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Return basic statistics about a DataFrame."""
    return {
        "shape": df.shape,
        "dtypes": df.dtypes,
        "missing": df.isnull().sum(),
        "describe": df.describe(include="all"),
    }


def detect_categorical_columns(df: pd.DataFrame, feature_cols: list[str]) -> list[str]:
    """Identify categorical (non-numeric) feature columns."""
    return [col for col in feature_cols if not pd.api.types.is_numeric_dtype(df[col])]


def preprocess_dataframe(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    encode_method: str = "onehot",
    scale_features: bool = False,
) -> tuple[np.ndarray, np.ndarray, list[str], LabelEncoder, StandardScaler | None]:
    """Preprocess a DataFrame for ML training.

    Returns (X, y, feature_names, target_encoder, scaler_or_None).
    """
    work = df[feature_cols + [target_col]].copy()

    # Fill missing values
    for col in feature_cols + [target_col]:
        if col not in work.columns:
            continue
        if work[col].dtype in ("object", "category") or not pd.api.types.is_numeric_dtype(work[col]):
            mode_vals = work[col].mode()
            work[col] = work[col].fillna(mode_vals.iloc[0] if not mode_vals.empty else "missing")
        else:
            work[col] = work[col].fillna(work[col].median())

    # Encode target
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(work[target_col])

    # Encode categorical features
    cat_cols = detect_categorical_columns(work, feature_cols)
    if cat_cols:
        if encode_method == "onehot":
            work = pd.get_dummies(work, columns=cat_cols, drop_first=False, dtype=float)
            final_feature_cols = [c for c in work.columns if c != target_col]
        else:
            for col in cat_cols:
                le = LabelEncoder()
                work[col] = le.fit_transform(work[col].astype(str))
            final_feature_cols = feature_cols
    else:
        final_feature_cols = feature_cols

    X = work[final_feature_cols].values.astype(float)

    # Scale
    scaler = None
    if scale_features:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    return X, y, final_feature_cols, target_encoder, scaler


def split_data(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into train and test sets with stratification."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def preprocess_split_data(
    X_train: np.ndarray,
    X_test: np.ndarray,
    scale_features: bool = False,
) -> tuple[np.ndarray, np.ndarray, StandardScaler | None]:
    """Apply scaling to pre-split data without data leakage."""
    scaler = None
    if scale_features:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
    return X_train, X_test, scaler
