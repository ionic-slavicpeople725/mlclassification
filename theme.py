"""Theme configuration and CSS injection for the ML Classification app."""

from __future__ import annotations

import streamlit as st

DARK_THEME = {
    "bg_primary": "#0a0e17",
    "bg_secondary": "#111827",
    "bg_card": "#1a1f2e",
    "bg_card_hover": "#222940",
    "border": "#2a3441",
    "border_accent": "#00d4aa33",
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent": "#00d4aa",
    "accent_dim": "#00d4aa22",
    "accent_glow": "#00d4aa44",
    "accent_secondary": "#6366f1",
    "accent_tertiary": "#f59e0b",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#6366f1",
    "plotly_bg": "rgba(10,14,23,0)",
    "plotly_paper": "rgba(10,14,23,0)",
    "plotly_grid": "#1e293b",
    "plotly_text": "#94a3b8",
    "plotly_palette": ["#00d4aa", "#6366f1", "#f59e0b", "#ef4444", "#ec4899", "#8b5cf6", "#14b8a6"],
    "cm_colorscale": [[0, "#0a0e17"], [0.5, "#134e4a"], [1, "#00d4aa"]],
    "highlight_best": "rgba(0, 212, 170, 0.15)",
}

LIGHT_THEME = {
    "bg_primary": "#f8fafc",
    "bg_secondary": "#f1f5f9",
    "bg_card": "#ffffff",
    "bg_card_hover": "#f1f5f9",
    "border": "#e2e8f0",
    "border_accent": "#0d9b7a33",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#94a3b8",
    "accent": "#0d9b7a",
    "accent_dim": "#0d9b7a15",
    "accent_glow": "#0d9b7a22",
    "accent_secondary": "#4f46e5",
    "accent_tertiary": "#d97706",
    "success": "#059669",
    "warning": "#d97706",
    "error": "#dc2626",
    "info": "#4f46e5",
    "plotly_bg": "rgba(248,250,252,0)",
    "plotly_paper": "rgba(248,250,252,0)",
    "plotly_grid": "#e2e8f0",
    "plotly_text": "#475569",
    "plotly_palette": ["#0d9b7a", "#4f46e5", "#d97706", "#dc2626", "#db2777", "#7c3aed", "#0891b2"],
    "cm_colorscale": [[0, "#f0fdfa"], [0.5, "#5eead4"], [1, "#0d9b7a"]],
    "highlight_best": "rgba(13, 155, 122, 0.12)",
}


def get_theme() -> dict[str, str]:
    """Return the current theme dict based on session state."""
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "dark"
    return DARK_THEME if st.session_state["theme_mode"] == "dark" else LIGHT_THEME


def render_theme_toggle() -> None:
    """Render a theme toggle in the sidebar."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    label = "Light Mode" if is_dark else "Dark Mode"
    icon = "sun" if is_dark else "moon"

    if st.sidebar.button(
        f"{'☀️' if is_dark else '🌙'}  Switch to {label}",
        key="theme_toggle",
        use_container_width=True,
    ):
        st.session_state["theme_mode"] = "light" if is_dark else "dark"
        st.rerun()


def inject_css() -> None:
    """Inject comprehensive custom CSS for the current theme."""
    t = get_theme()
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ─── ROOT OVERRIDES ─── */
:root {{
    --bg-primary: {t['bg_primary']};
    --bg-secondary: {t['bg_secondary']};
    --bg-card: {t['bg_card']};
    --border: {t['border']};
    --text-primary: {t['text_primary']};
    --text-secondary: {t['text_secondary']};
    --text-muted: {t['text_muted']};
    --accent: {t['accent']};
    --accent-dim: {t['accent_dim']};
    --accent-glow: {t['accent_glow']};
}}

/* ─── GLOBAL ─── */
.stApp, .stApp > header {{
    background-color: {t['bg_primary']} !important;
}}

.stMainBlockContainer {{
    padding-top: 2rem !important;
}}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {{
    background-color: {t['bg_primary']} !important;
    color: {t['text_primary']} !important;
}}

/* ─── TYPOGRAPHY ─── */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Outfit', sans-serif !important;
    color: {t['text_primary']} !important;
    letter-spacing: -0.02em;
}}

h1 {{
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    background: linear-gradient(135deg, {t['accent']}, {t['accent_secondary']}) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    padding-bottom: 0.1em !important;
}}

p, label, li {{
    font-family: 'Outfit', sans-serif !important;
    color: {t['text_primary']};
}}

/* Preserve material icons font for Streamlit icon elements */
[data-testid="stExpander"] details summary span[data-testid="stMarkdownContainer"],
[data-testid="stExpander"] details summary p {{
    font-family: 'Outfit', sans-serif !important;
}}

code, pre, .stCode {{
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: {t['bg_secondary']} !important;
    border-right: 1px solid {t['border']} !important;
}}

[data-testid="stSidebar"] h2 {{
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: {t['accent']} !important;
    -webkit-text-fill-color: {t['accent']} !important;
    background: none !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 1px solid {t['border']} !important;
}}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0 !important;
    background: {t['bg_secondary']} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid {t['border']} !important;
}}

.stTabs [data-baseweb="tab"] {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: {t['text_muted']} !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    background: transparent !important;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: {t['accent_dim']} !important;
    color: {t['accent']} !important;
    border: 1px solid {t['accent']}33 !important;
    box-shadow: 0 0 20px {t['accent_glow']} !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    display: none !important;
}}

.stTabs [data-baseweb="tab-border"] {{
    display: none !important;
}}

/* ─── CARDS / EXPANDERS ─── */
[data-testid="stExpander"] {{
    background: {t['bg_card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    overflow: hidden;
    transition: border-color 0.2s ease;
}}

[data-testid="stExpander"]:hover {{
    border-color: {t['accent']}44 !important;
}}

[data-testid="stExpander"] summary {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    color: {t['text_primary']} !important;
}}

/* ─── BUTTONS ─── */
.stButton > button {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.01em;
}}

.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, {t['accent']}, {t['accent_secondary']}) !important;
    color: #0a0e17 !important;
    border: none !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-size: 0.85rem !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 4px 24px {t['accent_glow']} !important;
}}

.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px {t['accent']}55 !important;
}}

/* Theme toggle button */
.stButton > button[kind="secondary"] {{
    background: {t['bg_card']} !important;
    color: {t['text_secondary']} !important;
    border: 1px solid {t['border']} !important;
    font-size: 0.8rem !important;
}}

.stButton > button[kind="secondary"]:hover {{
    border-color: {t['accent']}66 !important;
    color: {t['accent']} !important;
}}

/* ─── INPUTS / SELECT / SLIDER ─── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background-color: {t['bg_card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 10px !important;
    color: {t['text_primary']} !important;
}}

[data-baseweb="select"] {{
    background-color: {t['bg_card']} !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
    background-color: {t['accent']} !important;
    border-color: {t['accent']} !important;
}}

.stSlider [data-testid="stTickBar"] {{
    background: linear-gradient(90deg, {t['accent']}44, {t['accent']}) !important;
}}

/* ─── DATAFRAMES ─── */
[data-testid="stDataFrame"] {{
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}

/* ─── METRICS / ALERTS ─── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border: 1px solid {t['border']} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ─── PROGRESS BAR ─── */
.stProgress > div > div > div {{
    background: linear-gradient(90deg, {t['accent']}, {t['accent_secondary']}) !important;
    border-radius: 999px !important;
}}

.stProgress > div > div {{
    background: {t['bg_card']} !important;
    border-radius: 999px !important;
}}

/* ─── DOWNLOAD BUTTON ─── */
[data-testid="stDownloadButton"] > button {{
    background: {t['bg_card']} !important;
    border: 1px solid {t['accent']}44 !important;
    color: {t['accent']} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
}}

[data-testid="stDownloadButton"] > button:hover {{
    background: {t['accent_dim']} !important;
    border-color: {t['accent']} !important;
}}

/* ─── CHECKBOX / RADIO ─── */
[data-testid="stCheckbox"] label span {{
    color: {t['text_primary']} !important;
}}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] {{
    border: 2px dashed {t['border']} !important;
    border-radius: 12px !important;
    background: {t['bg_card']} !important;
    padding: 1rem !important;
}}

[data-testid="stFileUploader"]:hover {{
    border-color: {t['accent']}66 !important;
}}

/* ─── PLOTLY CHARTS ─── */
.stPlotlyChart {{
    background: {t['bg_card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
    margin-bottom: 1rem !important;
}}

/* ─── MULTISELECT TAGS ─── */
[data-baseweb="tag"] {{
    background-color: {t['accent_dim']} !important;
    border: 1px solid {t['accent']}44 !important;
    border-radius: 6px !important;
    color: {t['accent']} !important;
}}

[data-baseweb="tag"] span {{
    color: {t['accent']} !important;
}}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: {t['bg_primary']};
}}
::-webkit-scrollbar-thumb {{
    background: {t['border']};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {t['text_muted']};
}}

/* ─── DIVIDER ─── */
hr {{
    border-color: {t['border']} !important;
    opacity: 0.5;
}}

[data-testid="stSidebarSeparator"] {{
    background-color: {t['border']} !important;
}}

/* ─── FOOTER ─── */
.app-footer {{
    text-align: center;
    padding: 2rem 0 1.5rem 0;
    margin-top: 3rem;
    border-top: 1px solid {t['border']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: {t['text_muted']};
    letter-spacing: 0.04em;
}}

.app-footer a {{
    color: {t['accent']};
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.2s;
}}

.app-footer a:hover {{
    opacity: 0.8;
    text-decoration: underline;
}}

/* ─── HERO SUBTITLE ─── */
.hero-subtitle {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    color: {t['text_muted']} !important;
    letter-spacing: 0.03em;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
}}

/* ─── STATUS BADGES ─── */
.status-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}

.badge-ready {{
    background: {t['success']}22;
    color: {t['success']};
    border: 1px solid {t['success']}44;
}}

.badge-pending {{
    background: {t['warning']}22;
    color: {t['warning']};
    border: 1px solid {t['warning']}44;
}}

/* ─── METRIC CARDS ─── */
.metric-row {{
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
    flex-wrap: wrap;
}}

.metric-card {{
    flex: 1;
    min-width: 140px;
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    transition: border-color 0.2s ease, transform 0.2s ease;
}}

.metric-card:hover {{
    border-color: {t['accent']}44;
    transform: translateY(-2px);
}}

.metric-card .metric-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {t['text_muted']};
    margin-bottom: 0.35rem;
}}

.metric-card .metric-value {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: {t['accent']};
    line-height: 1.1;
}}

.metric-card .metric-detail {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {t['text_muted']};
    margin-top: 0.25rem;
}}

/* ─── SECTION HEADERS ─── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.5rem 0 0.75rem 0;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: {t['text_primary']};
}}

.section-header .section-icon {{
    font-size: 1.2rem;
}}

.section-header::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, {t['border']}, transparent);
    margin-left: 0.75rem;
}}

/* ─── ALGO TAG ─── */
.algo-tag {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    margin: 0.15rem;
    background: {t['accent_dim']};
    color: {t['accent']};
    border: 1px solid {t['accent']}33;
}}

/* ─── TRAINING TIME TABLE ─── */
.training-time-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 1rem;
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}}

.training-time-row:hover {{
    border-color: {t['accent']}44;
}}

.training-time-row .model-name {{
    font-family: 'Outfit', sans-serif;
    font-weight: 500;
    color: {t['text_primary']};
    font-size: 0.9rem;
}}

.training-time-row .time-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: {t['accent']};
    font-weight: 500;
}}

/* ─── ANIMATIONS ─── */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes pulse-glow {{
    0%, 100% {{ box-shadow: 0 0 10px {t['accent']}22; }}
    50% {{ box-shadow: 0 0 25px {t['accent']}44; }}
}}

.stTabs [data-baseweb="tab-panel"] > div {{
    animation: fadeInUp 0.3s ease-out;
}}

/* Light theme overrides — force light surfaces over Streamlit's dark base */
{"" if is_dark else f'''
.stApp, .stApp > header,
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{
    background-color: {t["bg_primary"]} !important;
    color: {t["text_primary"]} !important;
}}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {{
    background: {t["bg_secondary"]} !important;
    color: {t["text_primary"]} !important;
}}

[data-testid="stSidebar"] h2 {{
    color: {t["accent"]} !important;
    -webkit-text-fill-color: {t["accent"]} !important;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
    color: {t["text_primary"]} !important;
}}

/* Light sidebar border */
[data-testid="stSidebar"] {{
    border-right: 1px solid {t["border"]} !important;
}}

/* Sidebar collapse button */
[data-testid="stSidebar"] button[kind="header"] {{
    color: {t["text_primary"]} !important;
}}

/* Light selectboxes */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-baseweb="select"],
[data-baseweb="popover"] > div {{
    background-color: {t["bg_card"]} !important;
    color: {t["text_primary"]} !important;
    border-color: {t["border"]} !important;
}}

/* Light multiselect tags */
[data-baseweb="tag"] {{
    background-color: {t["accent_dim"]} !important;
    border: 1px solid {t["accent"]}44 !important;
    color: {t["accent"]} !important;
}}
[data-baseweb="tag"] span {{
    color: {t["accent"]} !important;
}}

/* Light input backgrounds */
input, textarea,
[data-baseweb="input"],
[data-baseweb="textarea"] {{
    background-color: {t["bg_card"]} !important;
    color: {t["text_primary"]} !important;
}}

/* Light expanders */
[data-testid="stExpander"] {{
    background: {t["bg_card"]} !important;
    border-color: {t["border"]} !important;
}}
[data-testid="stExpander"] summary span {{
    color: {t["text_primary"]} !important;
}}

/* Light dataframes */
[data-testid="stDataFrame"] {{
    background: {t["bg_card"]} !important;
}}

/* Light Plotly chart wrappers */
.stPlotlyChart {{
    background: {t["bg_card"]} !important;
    border-color: {t["border"]} !important;
}}

/* Light banner/header */
[data-testid="stHeader"] {{
    background: {t["bg_primary"]} !important;
}}

/* Button text */
[data-testid="stBaseButton-primary"] {{
    color: {t["bg_primary"]} !important;
}}

/* Light expander summary bar */
[data-testid="stExpander"] details,
[data-testid="stExpander"] details summary,
[data-testid="stExpander"] details > div {{
    background: {t["bg_card"]} !important;
    color: {t["text_primary"]} !important;
}}

/* Light sidebar multiselect dropdown */
[data-testid="stSidebar"] [data-baseweb="popover"] > div,
[data-testid="stSidebar"] [role="listbox"],
[data-testid="stSidebar"] [data-baseweb="menu"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {t["bg_card"]} !important;
    color: {t["text_primary"]} !important;
}}
[data-testid="stSidebar"] [role="option"] {{
    color: {t["text_primary"]} !important;
}}

/* Light tab list */
.stTabs [data-baseweb="tab-list"] {{
    background: {t["bg_secondary"]} !important;
    border-color: {t["border"]} !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {t["text_muted"]} !important;
}}
'''}
</style>
""", unsafe_allow_html=True)


def render_footer() -> None:
    """Render the powered-by footer."""
    st.markdown("""
<div class="app-footer">
    Powered by <a href="https://www.tertiaryinfotech.com" target="_blank" rel="noopener noreferrer">Tertiary Infotech Academy Pte Ltd</a>
</div>
""", unsafe_allow_html=True)


def render_metric_cards(metrics: dict[str, tuple[str, str]]) -> None:
    """Render custom metric cards.

    metrics: {label: (value, detail)}
    """
    cards_html = '<div class="metric-row">'
    for label, (value, detail) in metrics.items():
        cards_html += f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def render_section_header(icon: str, text: str) -> None:
    """Render a styled section header with icon."""
    st.markdown(f'<div class="section-header"><span class="section-icon">{icon}</span> {text}</div>', unsafe_allow_html=True)


def render_algo_tags(algos: list[str]) -> None:
    """Render algorithm names as styled tags."""
    tags = ''.join(f'<span class="algo-tag">{a}</span>' for a in algos)
    st.markdown(f'<div style="margin: 0.5rem 0;">{tags}</div>', unsafe_allow_html=True)


def render_training_time_rows(results: dict) -> None:
    """Render training times as styled rows."""
    for name, r in results.items():
        st.markdown(f"""
        <div class="training-time-row">
            <span class="model-name">{name}</span>
            <span class="time-val">{r['time']:.4f}s</span>
        </div>""", unsafe_allow_html=True)


def get_plotly_layout(t: dict | None = None) -> dict:
    """Return a Plotly layout config matching the current theme."""
    if t is None:
        t = get_theme()
    return {
        "paper_bgcolor": t["plotly_paper"],
        "plot_bgcolor": t["plotly_bg"],
        "font": {"family": "Outfit, sans-serif", "color": t["plotly_text"], "size": 13},
        "title_font": {"family": "Outfit, sans-serif", "size": 16, "color": t["text_primary"]},
        "xaxis": {
            "gridcolor": t["plotly_grid"],
            "zerolinecolor": t["plotly_grid"],
            "title_font": {"size": 12},
            "tickfont": {"family": "JetBrains Mono, monospace", "size": 11},
        },
        "yaxis": {
            "gridcolor": t["plotly_grid"],
            "zerolinecolor": t["plotly_grid"],
            "title_font": {"size": 12},
            "tickfont": {"family": "JetBrains Mono, monospace", "size": 11},
        },
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "JetBrains Mono, monospace", "size": 11},
        },
        "margin": {"l": 60, "r": 30, "t": 50, "b": 60},
    }
