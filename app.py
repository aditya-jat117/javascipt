from __future__ import annotations

import io
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="DataLens · CSV Explorer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = ["#7c5cff", "#27c7a5", "#ffb454", "#ff6687", "#49a6ff", "#bd78ed"]
PLOT_LAYOUT: dict[str, Any] = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, ui-sans-serif, system-ui", "color": "#e8eaf3", "size": 12},
    "margin": {"l": 12, "r": 12, "t": 24, "b": 12},
    "colorway": COLORS,
    "legend": {"bgcolor": "rgba(0,0,0,0)"},
    "hoverlabel": {"bgcolor": "#191b2a", "font_color": "#f8f8fc"},
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#f0f1f8; --muted:#9296ad; --panel:#151725; --line:rgba(255,255,255,.075); --violet:#9b86ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 80% 0%,rgba(112,79,226,.12),transparent 35%), #0c0e17; color:var(--ink); }
[data-testid="stHeader"] { background:rgba(12,14,23,.7); }
[data-testid="stSidebar"] { background:#10121d; border-right:1px solid var(--line); }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { font-family:Manrope,sans-serif; }
.block-container { padding-top:2.25rem; padding-bottom:3rem; max-width:1500px; }
.hero { padding:8px 0 25px; }
.eyebrow { color:#a899ff; text-transform:uppercase; letter-spacing:.17em; font-size:.72rem; font-weight:700; }
.hero h1 { font-family:Manrope,sans-serif; font-weight:800; letter-spacing:-.055em; line-height:1.05; font-size:clamp(2.2rem,4vw,3.65rem); margin:.55rem 0 .7rem; color:#f5f4fc; }
.hero p { color:#a3a7bc; font-size:1.02rem; margin:0; max-width:700px; }
.section-title { font-family:Manrope,sans-serif; font-size:1.18rem; font-weight:700; letter-spacing:-.025em; margin:.35rem 0 .15rem; }
.section-sub { color:var(--muted); font-size:.88rem; margin:0 0 1rem; }
.metric-card { background:linear-gradient(145deg,rgba(28,31,48,.95),rgba(19,21,33,.95)); border:1px solid var(--line); border-radius:16px; padding:18px 19px; min-height:112px; }
.metric-label { color:#a1a5bb; font-size:.78rem; font-weight:600; letter-spacing:.035em; }
.metric-value { font-family:Manrope,sans-serif; color:#f4f3fc; font-size:1.8rem; line-height:1.25; font-weight:800; margin-top:7px; }
.metric-note { color:#888da4; font-size:.76rem; margin-top:2px; }
.panel { background:linear-gradient(145deg,rgba(23,25,39,.94),rgba(17,19,30,.94)); border:1px solid var(--line); border-radius:18px; padding:18px 20px 10px; }
.pill { display:inline-block; border:1px solid rgba(155,134,255,.28); border-radius:999px; padding:5px 10px; color:#c0b5ff; font-size:.74rem; background:rgba(124,92,255,.08); }
div[data-testid="stTabs"] button { color:#a4a7b9; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#c6baff; }
div[data-testid="stFileUploader"] section { background:rgba(255,255,255,.025); border:1px dashed rgba(155,134,255,.35); border-radius:14px; }
.stDownloadButton button { border-radius:10px; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
small, .caption { color:var(--muted); }
</style>
""", unsafe_allow_html=True)


def read_csv(upload: Any, **kwargs: Any) -> pd.DataFrame:
    raw = upload.getvalue()
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=encoding, **kwargs)
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            last_error = exc
    raise ValueError(f"Could not read this CSV. Check its encoding and delimiter. Details: {last_error}")


def fmt_bytes(value: int) -> str:
    if value < 1024:
        return f"{value} B"
    if value < 1024**2:
        return f"{value / 1024:.1f} KB"
    return f"{value / 1024**2:.2f} MB"


def card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def chart_style(fig: go.Figure, height: int = 350) -> go.Figure:
    fig.update_layout(**PLOT_LAYOUT, height=height)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False, linecolor="rgba(255,255,255,.08)")
    return fig


def page_header() -> None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">Your data, in a clearer light</div>
      <h1>Meet your data.</h1>
      <p>Drop in a CSV and get a thoughtful, interactive read of what’s inside — from data quality to the patterns worth a closer look.</p>
    </div>
    """, unsafe_allow_html=True)


def render_dashboard(df: pd.DataFrame, source_name: str, file_size: int | None = None) -> None:
    if df.empty or len(df.columns) == 0:
        st.warning("This file has no rows or columns to analyze.")
        return
    rows, cols = df.shape
    numeric = list(df.select_dtypes(include="number").columns)
    categorical = list(df.select_dtypes(include=["object", "category", "bool", "string"]).columns)
    date_cols = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)
    missing_cells = int(df.isna().sum().sum())
    missing_pct = missing_cells / (rows * cols) * 100
    duplicates = int(df.duplicated().sum())

    st.markdown(f'<span class="pill">◈ &nbsp;{source_name}</span>', unsafe_allow_html=True)
    st.markdown("")
    k = st.columns(5)
    with k[0]: card("ROWS", f"{rows:,}", "records in this dataset")
    with k[1]: card("COLUMNS", f"{cols:,}", f"{len(numeric)} numeric · {len(categorical)} categorical")
    with k[2]: card("MISSING CELLS", f"{missing_pct:.1f}%", f"{missing_cells:,} empty values")
    with k[3]: card("DUPLICATE ROWS", f"{duplicates:,}", "exact row matches")
    with k[4]: card("FILE SIZE", fmt_bytes(file_size) if file_size is not None else "Loaded", "CSV source file")

    st.markdown("<br>", unsafe_allow_html=True)
    overview, quality, explore, relationship, data_tab = st.tabs(
        ["✦  Overview", "◉  Data quality", "▥  Explore columns", "⌁  Relationships", "▤  Data preview"]
    )

    with overview:
        st.markdown('<div class="section-title">A quick read</div><div class="section-sub">The shape, mix, and distribution of your dataset.</div>', unsafe_allow_html=True)
        left, right = st.columns([1.05, 1])
        with left:
            type_counts = pd.DataFrame({"Type": ["Numeric", "Categorical", "Date / time", "Other"], "Columns": [len(numeric), len(categorical), len(date_cols), cols-len(numeric)-len(categorical)-len(date_cols)]})
            fig = px.pie(type_counts, names="Type", values="Columns", hole=.70, color_discrete_sequence=COLORS)
            fig.update_traces(textposition="outside", textinfo="label+value", marker_line_color="#151725", marker_line_width=3)
            fig.add_annotation(text=f"{cols}<br><span style='font-size:11px;color:#9296ad'>columns</span>", x=.5, y=.5, showarrow=False, font={"size":22,"color":"#f4f3fc"})
            st.plotly_chart(chart_style(fig, 340), use_container_width=True, config={"displayModeBar": False})
        with right:
            if numeric:
                prof = pd.DataFrame({"Column": numeric, "Mean": [df[c].mean() for c in numeric], "Median": [df[c].median() for c in numeric]}).melt("Column", var_name="Measure", value_name="Value")
                fig = px.bar(prof, x="Column", y="Value", color="Measure", barmode="group", color_discrete_sequence=COLORS[0:2])
                fig.update_layout(xaxis_title="", yaxis_title="Value", legend_title="")
                st.plotly_chart(chart_style(fig, 340), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No numeric columns found. Try the Explore columns tab to chart categorical data.")
        if numeric:
            st.markdown('<div class="section-title">Numeric snapshot</div>', unsafe_allow_html=True)
            stats = df[numeric].describe().T.reset_index(names="Column")
            st.dataframe(stats, use_container_width=True, hide_index=True)

    with quality:
        st.markdown('<div class="section-title">Data quality</div><div class="section-sub">Spot incomplete fields and repeated records before drawing conclusions.</div>', unsafe_allow_html=True)
        missing = df.isna().sum().rename("Missing").to_frame()
        missing["Complete"] = rows - missing["Missing"]
        missing["Missing %"] = (missing["Missing"] / rows * 100).round(2)
        missing = missing.sort_values("Missing %", ascending=False)
        left, right = st.columns([1.15, .85])
        with left:
            if missing_cells:
                plot_missing = missing[missing["Missing"] > 0].reset_index(names="Column")
                fig = px.bar(plot_missing, x="Missing %", y="Column", orientation="h", color="Missing %", color_continuous_scale=["#27c7a5", "#7c5cff", "#ff6687"], hover_data=["Missing"])
                fig.update_layout(coloraxis_showscale=False, xaxis_title="Missing values (%)", yaxis_title="")
                st.plotly_chart(chart_style(fig, max(260, min(520, 42 * len(plot_missing)))), use_container_width=True, config={"displayModeBar": False})
            else:
                st.success("Lovely — there are no missing values in this dataset.")
        with right:
            st.markdown('<div class="section-title">Completeness by column</div>', unsafe_allow_html=True)
            st.dataframe(missing, use_container_width=True, height=350)
        if duplicates:
            st.warning(f"{duplicates:,} duplicate rows found. Review them in the preview before using this data for analysis.")
        else:
            st.success("No exact duplicate rows found.")
        constant = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
        if constant:
            st.info("Constant or near-empty columns: " + ", ".join(map(str, constant)))

    with explore:
        st.markdown('<div class="section-title">Explore a column</div><div class="section-sub">Choose a field to see its distribution, outliers, or most common values.</div>', unsafe_allow_html=True)
        column = st.selectbox("Column to explore", df.columns, key="explore_col")
        series = df[column]
        if pd.api.types.is_numeric_dtype(series):
            m1, m2, m3, m4 = st.columns(4)
            clean = series.dropna()
            with m1: card("AVERAGE", f"{clean.mean():,.3g}" if len(clean) else "—", f"{column}")
            with m2: card("MEDIAN", f"{clean.median():,.3g}" if len(clean) else "—", "50th percentile")
            with m3: card("RANGE", f"{clean.min():,.3g} – {clean.max():,.3g}" if len(clean) else "—", "min to max")
            with m4: card("UNIQUE", f"{series.nunique():,}", "distinct values")
            a, b = st.columns(2)
            with a:
                fig = px.histogram(df, x=column, nbins=35, marginal="box", color_discrete_sequence=COLORS)
                fig.update_layout(xaxis_title=str(column), yaxis_title="Count")
                st.plotly_chart(chart_style(fig, 370), use_container_width=True, config={"displayModeBar": False})
            with b:
                if len(clean):
                    fig = px.box(df, y=column, points="outliers", color_discrete_sequence=[COLORS[0]])
                    fig.update_layout(yaxis_title=str(column))
                    st.plotly_chart(chart_style(fig, 370), use_container_width=True, config={"displayModeBar": False})
        else:
            counts = series.astype("string").fillna("(missing)").value_counts().head(25).rename_axis("Value").reset_index(name="Count")
            st.caption(f"Showing up to 25 most common values · {series.nunique(dropna=True):,} unique values")
            fig = px.bar(counts.sort_values("Count"), x="Count", y="Value", orientation="h", color="Count", color_continuous_scale=["#40356e", "#9b86ff"])
            fig.update_layout(coloraxis_showscale=False, xaxis_title="Count", yaxis_title="")
            st.plotly_chart(chart_style(fig, max(320, min(650, 28 * len(counts)))), use_container_width=True, config={"displayModeBar": False})
            st.dataframe(counts, use_container_width=True, hide_index=True)

    with relationship:
        st.markdown('<div class="section-title">How do the columns move together?</div><div class="section-sub">Look for correlation between numeric fields or compare a numeric measure across groups.</div>', unsafe_allow_html=True)
        if len(numeric) >= 2:
            corr = df[numeric].corr(numeric_only=True)
            fig = px.imshow(corr, color_continuous_scale=[[0,"#fa718d"],[.5,"#222438"],[1,"#65d8bd"]], zmin=-1, zmax=1, text_auto=".2f", aspect="auto")
            fig.update_layout(coloraxis_colorbar_title="Correlation")
            st.plotly_chart(chart_style(fig, max(360, min(700, 55 * len(numeric)))), use_container_width=True, config={"displayModeBar": False})
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1: xcol = st.selectbox("X axis", numeric, key="rel_x")
            with c2: y_choices = [c for c in numeric if c != xcol] or numeric
            with c2: ycol = st.selectbox("Y axis", y_choices, key="rel_y")
            with c3: hue = st.selectbox("Color by (optional)", ["None"] + categorical, key="rel_hue")
            fig = px.scatter(df, x=xcol, y=ycol, color=None if hue == "None" else hue, color_discrete_sequence=COLORS, opacity=.78, trendline="ols" if len(df) >= 3 else None, hover_data=[c for c in df.columns if c not in (xcol, ycol)][:4])
            fig.update_layout(xaxis_title=str(xcol), yaxis_title=str(ycol))
            st.plotly_chart(chart_style(fig, 420), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Add at least two numeric columns to see correlations and scatter plots. You can still explore each column in the Explore columns tab.")

    with data_tab:
        st.markdown('<div class="section-title">Under the hood</div><div class="section-sub">Filter the preview and download a cleaned copy if you need one.</div>', unsafe_allow_html=True)
        search = st.text_input("Filter rows containing", placeholder="Type to search across all columns…", key="preview_search")
        preview = df
        if search:
            mask = df.astype("string").apply(lambda col: col.str.contains(search, case=False, na=False, regex=False)).any(axis=1)
            preview = df.loc[mask]
        st.caption(f"Showing {min(len(preview), 1000):,} of {len(preview):,} matching rows")
        st.dataframe(preview.head(1000), use_container_width=True, height=420)
        st.download_button("↓  Download data as CSV", data=df.to_csv(index=False).encode("utf-8"), file_name=f"{source_name.rsplit('.', 1)[0]}_export.csv", mime="text/csv")


def main() -> None:
    with st.sidebar:
        st.markdown("## ◈ DataLens")
        st.caption("An exploratory workspace for your CSV files.")
        st.markdown("---")
        uploaded = st.file_uploader("Choose a CSV file", type=["csv"], help="UTF-8 and common CSV formats are supported.")
        st.markdown("---")
        st.markdown("**A little guide**")
        st.caption("Start with Overview. Check Data quality for gaps, then Explore columns and Relationships to follow your curiosity.")
        st.markdown("<br><span class='caption'>Private by design · processed in this app session</span>", unsafe_allow_html=True)

    page_header()
    if uploaded is not None:
        try:
            df = read_csv(uploaded)
            render_dashboard(df, uploaded.name, uploaded.size)
        except Exception as exc:
            st.error(f"We couldn’t open that CSV: {exc}")
            st.info("Try saving the file as a standard comma-separated CSV and uploading it again.")
    else:
        st.markdown("""
        <div class="panel" style="padding:28px 30px;">
          <div class="eyebrow">Ready when you are</div>
          <div style="font:800 1.45rem Manrope,sans-serif;margin:.5rem 0;">Your first insight is one upload away.</div>
          <div style="color:#a3a7bc;max-width:650px;line-height:1.7;">Choose a CSV from the sidebar to see its structure, quality, distributions, and relationships. No setup or column mapping needed.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">What you’ll get</div>', unsafe_allow_html=True)
        c = st.columns(3)
        features = [("01", "A clear overview", "Row and column counts, missing values, duplicates, and a quick statistical snapshot."), ("02", "Interactive exploration", "Distributions, box plots, category counts, and searchable data preview."), ("03", "Relationships at a glance", "Correlation heatmaps and scatter plots that help reveal how measures move together.")]
        for col, (number, title, description) in zip(c, features):
            with col:
                st.markdown(f'<div class="metric-card"><div class="eyebrow">{number}</div><div style="font:700 1.06rem Manrope;margin:.6rem 0 .35rem">{title}</div><div style="color:#a3a7bc;font-size:.88rem;line-height:1.55">{description}</div></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
