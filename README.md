# ML Classification Algorithm Comparison Tool

An interactive Streamlit web application for comparing popular machine learning classification algorithms with rich visualizations.

## Features

- **7 algorithms**: Logistic Regression, SVM, Naive Bayes, Random Forest, XGBoost, KNN, Decision Tree
- **Flexible data loading**: Built-in datasets (Iris, Breast Cancer, Wine, Titanic), single CSV upload with configurable split, or separate train/test CSV uploads
- **Interactive hyperparameters**: Tune each algorithm via sidebar widgets
- **Comprehensive metrics**: Accuracy, Precision, Recall, F1-score, ROC-AUC with sortable comparison table
- **Rich visualizations**: Confusion matrices, ROC curves, Precision-Recall curves, feature importance, class distribution (Plotly)
- **Data preprocessing**: Automatic handling of missing values, categorical encoding (one-hot or label), optional feature scaling

## Quickstart

```bash
uv sync
uv run streamlit run app.py
```

## Project Structure

```
app.py              — Streamlit UI and orchestration
models.py           — Model definitions, training, evaluation
visualizations.py   — Plotly chart functions
data_loader.py      — Dataset loading and preprocessing
sample_data/        — Example CSV for upload testing
```

## Dependencies

- streamlit
- scikit-learn
- xgboost
- pandas / numpy
- matplotlib / seaborn
- plotly
