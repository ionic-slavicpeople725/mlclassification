"""Visualization functions using Plotly with theme support."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import (
    auc,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)
from sklearn.preprocessing import label_binarize

from theme import get_plotly_layout, get_theme


def _apply_layout(fig: go.Figure, **overrides: object) -> go.Figure:
    """Apply themed layout to a figure with optional overrides."""
    layout = get_plotly_layout()
    layout.update(overrides)
    fig.update_layout(**layout)
    return fig


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    model_name: str,
    normalized: bool = False,
) -> go.Figure:
    """Create a Plotly heatmap of the confusion matrix."""
    t = get_theme()
    cm = confusion_matrix(y_true, y_pred)
    if normalized:
        row_sums = cm.sum(axis=1, keepdims=True)
        cm = np.divide(cm, row_sums, where=row_sums != 0, out=np.zeros_like(cm, dtype=float))
        cm = np.round(cm, 3)
        fmt = ".2%"
    else:
        fmt = "d"

    text = [[f"{v:{fmt}}" if normalized else str(v) for v in row] for row in cm]

    fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=class_names,
            y=class_names,
            text=text,
            texttemplate="%{text}",
            textfont={"family": "JetBrains Mono, monospace", "size": 14, "color": t["text_primary"]},
            colorscale=t["cm_colorscale"],
            showscale=False,
            hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Value: %{text}<extra></extra>",
        )
    )
    _apply_layout(
        fig,
        title=f"<b>{model_name}</b>",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        height=380,
    )
    return fig


def plot_roc_curves(
    models_data: list[dict],
    class_names: list[str],
    is_binary: bool,
) -> go.Figure:
    """Overlay ROC curves for all models."""
    t = get_theme()
    palette = t["plotly_palette"]
    fig = go.Figure()
    n_classes = len(class_names)

    for idx, md in enumerate(models_data):
        if md["y_proba"] is None:
            continue
        y_true = md["y_true"]
        y_proba = md["y_proba"]
        name = md["name"]
        color = palette[idx % len(palette)]

        if is_binary:
            fpr, tpr, _ = roc_curve(y_true, y_proba[:, 1])
            roc_auc = auc(fpr, tpr)
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines",
                name=f"{name} (AUC={roc_auc:.3f})",
                line=dict(color=color, width=2.5),
                hovertemplate=f"{name}<br>FPR: %{{x:.3f}}<br>TPR: %{{y:.3f}}<extra></extra>",
            ))
        else:
            y_bin = label_binarize(y_true, classes=list(range(n_classes)))
            all_fpr = np.linspace(0, 1, 100)
            mean_tpr = np.zeros_like(all_fpr)
            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
                mean_tpr += np.interp(all_fpr, fpr, tpr)
            mean_tpr /= n_classes
            roc_auc = auc(all_fpr, mean_tpr)
            fig.add_trace(go.Scatter(
                x=all_fpr, y=mean_tpr, mode="lines",
                name=f"{name} (macro AUC={roc_auc:.3f})",
                line=dict(color=color, width=2.5),
            ))

    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        line=dict(dash="dot", color=t["text_muted"], width=1),
        name="Random baseline", showlegend=True,
    ))
    _apply_layout(
        fig,
        title="<b>ROC Curves</b>",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=480,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="JetBrains Mono, monospace", size=11)),
    )
    return fig


def plot_pr_curves(
    models_data: list[dict],
    class_names: list[str],
    is_binary: bool,
) -> go.Figure:
    """Overlay Precision-Recall curves for all models."""
    t = get_theme()
    palette = t["plotly_palette"]
    fig = go.Figure()
    n_classes = len(class_names)

    for idx, md in enumerate(models_data):
        if md["y_proba"] is None:
            continue
        y_true = md["y_true"]
        y_proba = md["y_proba"]
        name = md["name"]
        color = palette[idx % len(palette)]

        if is_binary:
            precision, recall, _ = precision_recall_curve(y_true, y_proba[:, 1])
            pr_auc = auc(recall, precision)
            fig.add_trace(go.Scatter(
                x=recall, y=precision, mode="lines",
                name=f"{name} (AUC={pr_auc:.3f})",
                line=dict(color=color, width=2.5),
            ))
        else:
            y_bin = label_binarize(y_true, classes=list(range(n_classes)))
            all_recall = np.linspace(0, 1, 100)
            mean_precision = np.zeros_like(all_recall)
            for i in range(n_classes):
                precision, recall, _ = precision_recall_curve(y_bin[:, i], y_proba[:, i])
                sorted_idx = np.argsort(recall)
                mean_precision += np.interp(all_recall, recall[sorted_idx], precision[sorted_idx])
            mean_precision /= n_classes
            pr_auc = auc(all_recall, mean_precision)
            fig.add_trace(go.Scatter(
                x=all_recall, y=mean_precision, mode="lines",
                name=f"{name} (macro AUC={pr_auc:.3f})",
                line=dict(color=color, width=2.5),
            ))

    _apply_layout(
        fig,
        title="<b>Precision-Recall Curves</b>",
        xaxis_title="Recall",
        yaxis_title="Precision",
        height=480,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="JetBrains Mono, monospace", size=11)),
    )
    return fig


def plot_feature_importance(
    importance_df: pd.DataFrame,
    model_name: str,
    top_n: int = 15,
) -> go.Figure:
    """Horizontal bar chart of top N feature importances."""
    t = get_theme()
    df = importance_df.head(top_n).iloc[::-1]

    max_val = df["importance"].max() if len(df) > 0 else 1
    colors = [f"rgba({int(t['accent'].lstrip('#')[0:2], 16)}, {int(t['accent'].lstrip('#')[2:4], 16)}, {int(t['accent'].lstrip('#')[4:6], 16)}, {0.4 + 0.6 * (v / max_val)})" for v in df["importance"]]

    fig = go.Figure(
        go.Bar(
            x=df["importance"], y=df["feature"], orientation="h",
            marker=dict(color=colors, line=dict(color=t["accent"], width=1)),
            hovertemplate="%{y}: %{x:.4f}<extra></extra>",
        )
    )
    _apply_layout(
        fig,
        title=f"<b>{model_name}</b>",
        xaxis_title="Importance",
        yaxis_title="",
        height=max(300, min(top_n, len(df)) * 30 + 80),
    )
    return fig


def plot_class_distribution(
    y_train: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
) -> go.Figure:
    """Grouped bar chart of class distribution in train vs test."""
    t = get_theme()
    train_counts = pd.Series(y_train).value_counts().sort_index()
    test_counts = pd.Series(y_test).value_counts().sort_index()
    labels = [class_names[i] if i < len(class_names) else str(i) for i in train_counts.index]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=train_counts.values, name="Train",
        marker=dict(color=t["accent"], line=dict(width=0)),
        hovertemplate="Train — %{x}: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=labels, y=test_counts.values, name="Test",
        marker=dict(color=t["accent_secondary"], line=dict(width=0)),
        hovertemplate="Test — %{x}: %{y}<extra></extra>",
    ))
    _apply_layout(
        fig,
        title="<b>Class Distribution</b>",
        xaxis_title="Class",
        yaxis_title="Count",
        barmode="group",
        height=380,
        bargap=0.25,
        bargroupgap=0.1,
    )
    return fig


def plot_metrics_comparison(results_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing all models across metrics."""
    t = get_theme()
    palette = t["plotly_palette"]
    metric_cols = [c for c in results_df.columns if c not in ("Model", "Training Time (s)")]
    fig = go.Figure()

    for i, col in enumerate(metric_cols):
        fig.add_trace(go.Bar(
            x=results_df["Model"], y=results_df[col], name=col,
            marker=dict(color=palette[i % len(palette)]),
            hovertemplate=f"{col}<br>%{{x}}: %{{y:.4f}}<extra></extra>",
        ))

    _apply_layout(
        fig,
        title="<b>Model Comparison</b>",
        xaxis_title="",
        yaxis_title="Score",
        barmode="group",
        height=480,
        bargap=0.2,
        bargroupgap=0.05,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono, monospace", size=10),
        ),
    )
    return fig
