"""ML Classification Algorithm Comparison Tool — Streamlit App."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from data_loader import (
    BUILTIN_DATASETS,
    detect_categorical_columns,
    get_dataset_stats,
    load_builtin_dataset,
    load_uploaded_csv,
    preprocess_dataframe,
    preprocess_split_data,
    split_data,
)
from models import (
    ALGORITHM_DESCRIPTIONS,
    build_model,
    evaluate_model,
    get_classification_report_df,
    get_feature_importance,
    get_hyperparameter_specs,
    train_model,
)
from theme import (
    get_theme,
    inject_css,
    render_algo_tags,
    render_footer,
    render_metric_cards,
    render_section_header,
    render_theme_toggle,
    render_training_time_rows,
)
from visualizations import (
    plot_class_distribution,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_metrics_comparison,
    plot_pr_curves,
    plot_roc_curves,
)

ALGORITHMS = list(ALGORITHM_DESCRIPTIONS.keys())


def render_sidebar() -> tuple[list[str], dict[str, dict]]:
    """Render sidebar with theme toggle, algorithm selection, and hyperparameters."""
    # Theme toggle at top
    render_theme_toggle()
    st.sidebar.markdown("---")

    st.sidebar.header("Algorithm Selection")
    selected = st.sidebar.multiselect(
        "Select algorithms to compare",
        ALGORITHMS,
        default=["Logistic Regression", "Random Forest"],
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Hyperparameters")

    specs = get_hyperparameter_specs()
    all_params: dict[str, dict] = {}

    for algo in selected:
        with st.sidebar.expander(f"{algo}", expanded=False):
            st.caption(ALGORITHM_DESCRIPTIONS[algo])
            params: dict = {}
            for spec in specs.get(algo, []):
                key = f"{algo}_{spec['param']}"
                if spec["type"] == "slider":
                    kwargs: dict = {
                        "label": spec["param"],
                        "min_value": spec["min"],
                        "max_value": spec["max"],
                        "value": spec["default"],
                        "step": spec.get("step", 1),
                        "key": key,
                    }
                    if "format" in spec:
                        kwargs["format"] = spec["format"]

                    val = st.slider(**kwargs)

                    if spec.get("allow_none"):
                        use_none = st.checkbox(f"Set {spec['param']} = None (unlimited)", key=f"{key}_none")
                        if use_none:
                            val = None

                    params[spec["param"]] = val

                elif spec["type"] == "selectbox":
                    val = st.selectbox(
                        spec["param"],
                        spec["options"],
                        index=spec["options"].index(spec["default"]),
                        key=key,
                    )
                    params[spec["param"]] = val

                elif spec["type"] == "select_slider":
                    exponents = list(range(spec["min"], spec["max"] + 1))
                    values = [10.0**e for e in exponents]
                    default_val = 10.0 ** spec["default"]
                    val = st.select_slider(
                        spec["param"],
                        options=values,
                        value=default_val,
                        format_func=lambda x: f"{x:.1e}",
                        key=key,
                    )
                    params[spec["param"]] = val

            all_params[algo] = params

    return selected, all_params


def render_data_tab() -> None:
    """Render the Data tab for loading and configuring datasets."""
    render_section_header("\u25c8", "Data Source")

    source = st.radio(
        "Data source",
        ["Built-in dataset", "Upload single CSV", "Upload train & test CSVs"],
        horizontal=True,
        label_visibility="collapsed",
    )

    df = None
    df_train = None
    df_test = None
    target_col = None
    separate_files = False

    if source == "Built-in dataset":
        dataset_name = st.selectbox("Choose a dataset", BUILTIN_DATASETS)
        df, target_col = load_builtin_dataset(dataset_name)
        render_metric_cards({
            "Dataset": (dataset_name, "Built-in"),
            "Rows": (str(df.shape[0]), "samples"),
            "Columns": (str(df.shape[1]), "features + target"),
        })

    elif source == "Upload single CSV":
        file = st.file_uploader("Upload a CSV file", type=["csv"], key="single_csv")
        if file is not None:
            try:
                df = load_uploaded_csv(file)
                render_metric_cards({
                    "Dataset": (file.name, "Uploaded"),
                    "Rows": (str(df.shape[0]), "samples"),
                    "Columns": (str(df.shape[1]), "columns"),
                })
            except ValueError as e:
                st.error(str(e))
                return

    elif source == "Upload train & test CSVs":
        separate_files = True
        col1, col2 = st.columns(2)
        with col1:
            train_file = st.file_uploader("Training CSV", type=["csv"], key="train_csv")
        with col2:
            test_file = st.file_uploader("Testing CSV", type=["csv"], key="test_csv")
        if train_file is not None and test_file is not None:
            try:
                df_train = load_uploaded_csv(train_file)
                df_test = load_uploaded_csv(test_file)
                if set(df_train.columns) != set(df_test.columns):
                    st.error("Train and test files must have the same columns.")
                    return
                df = df_train
                render_metric_cards({
                    "Train": (str(df_train.shape[0]), "samples"),
                    "Test": (str(df_test.shape[0]), "samples"),
                    "Columns": (str(df_train.shape[1]), "columns"),
                })
            except ValueError as e:
                st.error(str(e))
                return

    if df is None:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; opacity: 0.5;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">&#9650;</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                Select a built-in dataset or upload a CSV to begin
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Store raw dataframe
    st.session_state["raw_df"] = df
    st.session_state["separate_files"] = separate_files
    if separate_files:
        st.session_state["raw_df_train"] = df_train
        st.session_state["raw_df_test"] = df_test

    # Data preview
    render_section_header("\u229e", "Preview")
    with st.expander("Data Preview", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    # Stats
    stats = get_dataset_stats(df)
    with st.expander("Dataset Statistics"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Shape:** `{stats['shape'][0]}` rows \u00d7 `{stats['shape'][1]}` columns")
            st.markdown("**Column Types:**")
            st.dataframe(stats["dtypes"].to_frame("Type"), use_container_width=True)
        with col2:
            missing = stats["missing"]
            if missing.sum() > 0:
                st.markdown("**Missing Values:**")
                st.dataframe(missing[missing > 0].to_frame("Count"), use_container_width=True)
            else:
                st.markdown('<span class="status-badge badge-ready">No Missing Values</span>', unsafe_allow_html=True)

    # Target and feature selection
    render_section_header("\u2b29", "Column Configuration")

    if target_col is None:
        target_col = st.selectbox("Target column", df.columns.tolist())
    else:
        target_col = st.selectbox("Target column", df.columns.tolist(), index=df.columns.tolist().index(target_col))

    available_features = [c for c in df.columns if c != target_col]
    feature_cols = st.multiselect("Feature columns", available_features, default=available_features)

    if not feature_cols:
        st.warning("Select at least one feature column.")
        return

    # Check unique classes
    n_classes = df[target_col].nunique()
    if n_classes < 2:
        st.error("Target column must have at least 2 unique classes.")
        return

    # Encoding options
    cat_cols = detect_categorical_columns(df, feature_cols)
    col1, col2 = st.columns(2)
    with col1:
        if cat_cols:
            encode_method = st.radio(
                "Categorical encoding",
                ["onehot", "label"],
                format_func=lambda x: "One-Hot Encoding" if x == "onehot" else "Label Encoding",
                help=f"Categorical columns: {', '.join(cat_cols)}",
            )
        else:
            encode_method = "onehot"
            st.markdown('<span class="status-badge badge-ready">All Numeric</span>', unsafe_allow_html=True)
    with col2:
        scale_features = st.checkbox("Scale features (StandardScaler)", value=False)

    # Train/test split
    if not separate_files:
        test_size = st.slider("Test set ratio", 0.1, 0.5, 0.2, 0.05)
    else:
        test_size = None

    # Process data
    try:
        if separate_files and df_train is not None and df_test is not None:
            X_train_raw, y_train, feat_names, target_enc, _ = preprocess_dataframe(
                df_train, target_col, feature_cols, encode_method, scale_features=False
            )
            X_test_raw, y_test, feat_names_test, _, _ = preprocess_dataframe(
                df_test, target_col, feature_cols, encode_method, scale_features=False
            )
            X_train, X_test, scaler = preprocess_split_data(X_train_raw, X_test_raw, scale_features)
        else:
            X, y, feat_names, target_enc, _ = preprocess_dataframe(
                df, target_col, feature_cols, encode_method, scale_features=False
            )
            X_train_raw, X_test_raw, y_train, y_test = split_data(X, y, test_size=test_size)
            X_train, X_test, scaler = preprocess_split_data(X_train_raw, X_test_raw, scale_features)

        class_names = [str(c) for c in target_enc.classes_]
        is_binary = len(class_names) == 2

        # Store in session state
        st.session_state.update({
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "feature_names": feat_names,
            "class_names": class_names,
            "is_binary": is_binary,
            "n_classes": len(class_names),
            "data_ready": True,
        })

        render_metric_cards({
            "Train": (str(X_train.shape[0]), "samples"),
            "Test": (str(X_test.shape[0]), "samples"),
            "Features": (str(X_train.shape[1]), "dimensions"),
            "Classes": (str(len(class_names)), "binary" if is_binary else "multiclass"),
        })

    except Exception as e:
        st.error(f"Preprocessing error: {e}")
        st.session_state["data_ready"] = False


def render_training_tab(selected_algos: list[str], all_params: dict[str, dict]) -> None:
    """Render the Training tab."""
    if not st.session_state.get("data_ready"):
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; opacity: 0.5;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">&#9881;</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                Configure your data in the Data tab first
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not selected_algos:
        st.warning("Select at least one algorithm in the sidebar.")
        return

    render_section_header("\u2b50", "Selected Models")
    render_algo_tags(selected_algos)

    st.markdown("")
    if st.button("TRAIN MODELS", type="primary", use_container_width=True):
        X_train = st.session_state["X_train"]
        y_train = st.session_state["y_train"]
        X_test = st.session_state["X_test"]
        y_test = st.session_state["y_test"]
        class_names = st.session_state["class_names"]
        feature_names = st.session_state["feature_names"]
        n_classes = st.session_state["n_classes"]

        results: dict[str, dict] = {}
        trained_models: dict = {}
        progress = st.progress(0, text="Initializing...")

        for i, algo in enumerate(selected_algos):
            progress.progress((i) / len(selected_algos), text=f"Training {algo}...")
            try:
                params = all_params.get(algo, {})
                model = build_model(algo, params, n_classes=n_classes)
                fitted, elapsed = train_model(model, X_train, y_train)
                metrics = evaluate_model(fitted, X_test, y_test, class_names)
                importance = get_feature_importance(fitted, feature_names)

                results[algo] = {
                    "metrics": {k: v for k, v in metrics.items() if k not in ("y_pred", "y_proba")},
                    "y_pred": metrics["y_pred"],
                    "y_proba": metrics["y_proba"],
                    "time": elapsed,
                    "importance": importance,
                }
                trained_models[algo] = fitted
            except Exception as e:
                st.error(f"Error training {algo}: {e}")

        progress.progress(1.0, text="Complete")

        st.session_state["results"] = results
        st.session_state["trained_models"] = trained_models
        st.session_state["training_complete"] = True

    # Show training times
    if st.session_state.get("training_complete"):
        results = st.session_state["results"]
        render_section_header("\u23f1", "Training Performance")
        render_training_time_rows(results)

        # Quick accuracy overview
        render_section_header("\u2713", "Quick Results")
        acc_cards = {}
        for name, r in results.items():
            acc = r["metrics"]["Accuracy"]
            acc_cards[name] = (f"{acc:.1%}", f"F1={r['metrics']['F1 (weighted)']:.3f}")
        render_metric_cards(acc_cards)


def render_metrics_tab() -> None:
    """Render the Metrics tab with comparison table."""
    if not st.session_state.get("training_complete"):
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; opacity: 0.5;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">&#9632;</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                Train models first in the Training tab
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    t = get_theme()
    results = st.session_state["results"]

    # Build comparison table
    rows = []
    for name, r in results.items():
        row = {"Model": name}
        row.update(r["metrics"])
        row["Training Time (s)"] = round(r["time"], 4)
        rows.append(row)

    df = pd.DataFrame(rows)
    metric_cols = [c for c in df.columns if c not in ("Model", "Training Time (s)")]

    render_section_header("\u2263", "Model Comparison")

    def highlight_max(s: pd.Series) -> list[str]:
        is_max = s == s.max()
        return [f"background-color: {t['highlight_best']}" if v else "" for v in is_max]

    styled = df.style.apply(
        lambda s: highlight_max(s) if s.name in metric_cols else [""] * len(s),
        axis=0,
    ).format({c: "{:.4f}" for c in metric_cols}).format({"Training Time (s)": "{:.4f}"})

    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Download button
    csv = df.to_csv(index=False)
    st.download_button("Download results as CSV", csv, "model_comparison.csv", "text/csv")

    # Comparison chart
    render_section_header("\u2261", "Visual Comparison")
    chart_df = df[["Model"] + [c for c in metric_cols if c != "ROC-AUC" or df[c].notna().all()]].copy()
    fig = plot_metrics_comparison(chart_df)
    st.plotly_chart(fig, use_container_width=True)


def render_visualizations_tab() -> None:
    """Render the Visualizations tab."""
    if not st.session_state.get("training_complete"):
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; opacity: 0.5;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">&#9670;</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                Train models first in the Training tab
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    results = st.session_state["results"]
    y_test = st.session_state["y_test"]
    class_names = st.session_state["class_names"]
    is_binary = st.session_state["is_binary"]
    y_train = st.session_state["y_train"]
    model_names = list(results.keys())

    # Class Distribution
    render_section_header("\u2593", "Class Distribution")
    fig = plot_class_distribution(y_train, y_test, class_names)
    st.plotly_chart(fig, use_container_width=True)

    # Confusion Matrices
    render_section_header("\u25a6", "Confusion Matrices")
    normalized = st.checkbox("Show normalized", value=False, key="cm_norm")
    cols = st.columns(min(len(model_names), 3))
    for i, name in enumerate(model_names):
        with cols[i % len(cols)]:
            fig = plot_confusion_matrix(y_test, results[name]["y_pred"], class_names, name, normalized)
            st.plotly_chart(fig, use_container_width=True)

    # ROC Curves
    render_section_header("\u2197", "ROC Curves")
    models_data = [
        {"name": name, "y_true": y_test, "y_proba": results[name]["y_proba"]}
        for name in model_names
    ]
    fig = plot_roc_curves(models_data, class_names, is_binary)
    st.plotly_chart(fig, use_container_width=True)

    # Precision-Recall Curves
    render_section_header("\u2194", "Precision-Recall Curves")
    fig = plot_pr_curves(models_data, class_names, is_binary)
    st.plotly_chart(fig, use_container_width=True)

    # Feature Importance
    render_section_header("\u2191", "Feature Importance")
    importance_cols = st.columns(min(len(model_names), 2))
    col_idx = 0
    for name in model_names:
        importance = results[name].get("importance")
        if importance is not None:
            with importance_cols[col_idx % len(importance_cols)]:
                fig = plot_feature_importance(importance, name)
                st.plotly_chart(fig, use_container_width=True)
            col_idx += 1

    if col_idx == 0:
        st.info("No feature importance available for the selected models.")

    # Classification Reports
    render_section_header("\u2630", "Classification Reports")
    for name in model_names:
        with st.expander(f"{name}"):
            report_df = get_classification_report_df(y_test, results[name]["y_pred"], class_names)
            st.dataframe(report_df, use_container_width=True)


def main() -> None:
    """Main entry point."""
    st.set_page_config(
        page_title="ML Classification Lab",
        page_icon="\u25c8",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    for key in ("data_ready", "training_complete"):
        if key not in st.session_state:
            st.session_state[key] = False

    # Inject theme CSS
    inject_css()

    # Header
    st.markdown('<h1>ML Classification Lab</h1>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare classification algorithms side-by-side with interactive analysis</div>', unsafe_allow_html=True)

    # Sidebar
    selected_algos, all_params = render_sidebar()

    # Main tabs
    tab_data, tab_train, tab_metrics, tab_viz = st.tabs(
        ["\u25c8  Data", "\u25b6  Training", "\u2261  Metrics", "\u25c6  Visualizations"]
    )

    with tab_data:
        render_data_tab()

    with tab_train:
        render_training_tab(selected_algos, all_params)

    with tab_metrics:
        render_metrics_tab()

    with tab_viz:
        render_visualizations_tab()

    # Footer
    render_footer()


if __name__ == "__main__":
    main()
