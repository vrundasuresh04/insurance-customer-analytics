from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Insurance Customer Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#15324B"
NAVY_DARK = "#10283D"
TEAL = "#148A86"
TEAL_LIGHT = "#E4F3F1"
CORAL = "#E58B69"
MUTED = "#66788A"

st.markdown(
    f"""
    <style>
      :root {{ --navy: {NAVY}; --teal: {TEAL}; --coral: {CORAL}; }}
      .stApp {{ background: #F3F6FA; }}
      [data-testid="stHeader"] {{ background: rgba(243,246,250,.92); }}
      [data-testid="stSidebar"] {{
        background: linear-gradient(165deg, {NAVY_DARK} 0%, #17435B 100%);
      }}
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] h1,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3,
      [data-testid="stSidebar"] small {{ color: #F1F6FA !important; }}
      [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: #FFFFFF; border: 1px solid #D8E2EA; border-radius: 9px;
      }}
      [data-testid="stSidebar"] [data-baseweb="select"] span {{ color: #19364F; }}
      [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18);
        border-radius: 12px; padding: 10px;
      }}
      [data-testid="stSidebar"] button[kind="primary"] {{
        background: #78D2C7 !important; color: #10283D !important;
        border: 1px solid #78D2C7 !important; font-weight: 700 !important;
        opacity: 1 !important; border-radius: 9px !important;
      }}
      [data-testid="stSidebar"] button[kind="primary"]:hover {{
        background: #9BE2D8 !important; border-color: #9BE2D8 !important;
      }}
      h1, h2, h3 {{ color: {NAVY}; letter-spacing: -.02em; }}
      [data-testid="stMetric"] {{ background: #FFFFFF; padding: 19px 20px;
        border: 1px solid #E1E8EF; border-top: 3px solid {TEAL};
        border-radius: 14px; box-shadow: 0 5px 18px rgba(21,50,75,.055); }}
      [data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: .88rem; }}
      [data-testid="stMetricValue"] {{ color: {NAVY}; font-weight: 700; }}
      [data-testid="stPlotlyChart"] {{ background: #FFFFFF; border-radius: 14px; }}
      div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {{ gap: 1.1rem; }}
      .hero {{ background: linear-gradient(112deg, {NAVY_DARK} 0%, #17435B 68%, {TEAL} 145%);
        border-radius: 18px; padding: 26px 32px; margin: 3px 0 22px 0;
        box-shadow: 0 10px 28px rgba(16,40,61,.16); }}
      .hero-kicker {{ color: #A9DED8; font-size: .76rem; font-weight: 700;
        letter-spacing: .15em; text-transform: uppercase; margin-bottom: 7px; }}
      .hero-title {{ color: #FFFFFF; font-size: 2rem; line-height: 1.2;
        font-weight: 750; margin: 0; }}
      .hero-sub {{ color: #D8E7EF; font-size: 1rem; margin: 7px 0 0 0; }}
      .section-label {{ color: {NAVY}; font-size: 1.25rem; font-weight: 700;
        margin: 17px 0 7px 0; }}
      .insight-card {{ background: #FFFFFF; border: 1px solid #E1E8EF;
        border-left: 4px solid {CORAL}; border-radius: 12px; padding: 15px 17px;
        height: 100%; box-shadow: 0 4px 14px rgba(21,50,75,.045); color: {NAVY}; }}
      .insight-label {{ color: {MUTED}; font-size: .78rem; font-weight: 700;
        letter-spacing: .06em; text-transform: uppercase; margin-bottom: 7px; }}
      .insight-value {{ font-size: 1.1rem; font-weight: 700; }}
      .footnote {{ color: {MUTED}; font-size: .84rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def read_data(file_bytes=None):
    if file_bytes is not None:
        from io import BytesIO
        data = pd.read_csv(BytesIO(file_bytes))
    else:
        path = Path(__file__).with_name("ticdata2000_with_headers.csv")
        if not path.exists():
            return None
        data = pd.read_csv(path)
    return data.loc[:, ~data.columns.astype(str).str.match(r"^Unnamed")]


uploaded = st.sidebar.file_uploader("Dataset CSV", type=["csv"])
df = read_data(uploaded.getvalue() if uploaded else None)

if df is None:
    st.title("Insurance Customer Analytics")
    st.info("Place `ticdata2000_with_headers.csv` beside `app.py`, or upload it in the sidebar.")
    st.stop()

required = {"CARAVAN", "MGEMLEEF", "MINKGEM", "MAUT0", "MOSHOOFD", "MRELGE"}
missing = sorted(required - set(df.columns))
if missing:
    st.error("This CSV is missing expected columns: " + ", ".join(missing))
    st.stop()

# Prepare honest, clearly labeled metrics and groupings from the source columns.
df = df.copy()
df["Caravan status"] = df["CARAVAN"].map({0: "No caravan policy", 1: "Has caravan policy"})
policy_count_cols = [c for c in df.columns if c.startswith("A") and c != "CARAVAN"]
df["Other policy count"] = df[policy_count_cols].fillna(0).sum(axis=1)
df["Other policy group"] = pd.cut(
    df["Other policy count"], bins=[-1, 0, 1, 3, float("inf")],
    labels=["0", "1", "2–3", "4+"],
)

st.markdown(
    f'<div class="hero"><div class="hero-kicker">Customer portfolio • benchmark analysis</div>'
    f'<div class="hero-title">Insurance Customer Analytics</div>'
    f'<div class="hero-sub">Explore caravan policy patterns across {len(df):,} training customer records</div></div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("## Report filters")
st.sidebar.caption("Set code ranges for the customer cohort. Policy status filters the count charts only; purchase rates continue to compare both outcomes.")

filter_specs = [
    ("Customer main type", "MOSHOOFD", "Coded customer-type category."),
    ("Area age profile", "MGEMLEEF", "Coded area-level average age category, not exact customer age."),
    ("Area income profile", "MINKGEM", "Coded average income category for the customer's area."),
    ("Area vehicle profile", "MAUT0", "Coded area-level vehicle profile, not this customer's vehicle count."),
    ("Area relationship profile", "MRELGE", "Coded area-level relationship profile."),
]


def full_range(column):
    values = sorted(df[column].dropna().unique().tolist())
    return (values[0], values[-1])


if st.sidebar.button("Reset filters", use_container_width=True, type="primary"):
    for _, column, _ in filter_specs:
        st.session_state[f"range_{column}"] = full_range(column)
    st.session_state["filter_caravan_status"] = "All statuses"
    st.rerun()


def add_code_filter(label, column, help_text):
    values = sorted(df[column].dropna().unique().tolist())
    selected_range = st.sidebar.select_slider(
        label,
        options=values,
        value=full_range(column),
        key=f"range_{column}",
        help=help_text,
    )
    lower, upper = selected_range
    return df[column].between(lower, upper)


profile_filtered = df
for label, col, help_text in filter_specs:
    mask = add_code_filter(label, col, help_text)
    profile_filtered = profile_filtered[mask.loc[profile_filtered.index]]

status = st.sidebar.selectbox(
    "Caravan policy status", ["All statuses", "Has caravan policy", "No caravan policy"],
    index=0, key="filter_caravan_status"
)
filtered = profile_filtered
if status != "All statuses":
    filtered = filtered[filtered["Caravan status"] == status]
if profile_filtered.empty:
    st.warning("No customers match these selections. Choose All categories or another filter value.")
    st.stop()

n_customers = len(profile_filtered)
n_holders = int(profile_filtered["CARAVAN"].sum())
purchase_rate = n_holders / n_customers if n_customers else 0
avg_products = profile_filtered["Other policy count"].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Customers in selection", f"{n_customers:,}")
m2.metric("Caravan policyholders", f"{n_holders:,}")
m3.metric("Caravan purchase rate", f"{purchase_rate:.2%}")
m4.metric("Avg. other product policies", f"{avg_products:.2f}")

st.markdown(
    '<div class="footnote">Age, income, relationship, and vehicle profile fields describe customer areas. '
    'They are coded categories, not exact individual customer details. This dataset has no policy-tenure field.</div>',
    unsafe_allow_html=True,
)


def polish_chart(fig, percent_axis=False):
    fig.update_layout(
        title_font=dict(size=16, color=NAVY),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#46596C", size=12),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        margin=dict(l=18, r=18, t=58, b=72),
        xaxis=dict(title_font=dict(color=MUTED), tickfont=dict(color=MUTED), showgrid=False),
        yaxis=dict(title_font=dict(color=MUTED), tickfont=dict(color=MUTED),
                   gridcolor="#E9EEF3", zerolinecolor="#E9EEF3"),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5,
                    title_text="", font=dict(size=11)),
        hoverlabel=dict(bgcolor=NAVY, font_color="#FFFFFF"),
    )
    if percent_axis:
        fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    return fig


def rate_chart(column, title, x_label):
    grouped = profile_filtered.groupby(column, observed=True).agg(
        customers=("CARAVAN", "size"), holders=("CARAVAN", "sum")
    ).reset_index()
    grouped["purchase_rate"] = grouped["holders"] / grouped["customers"]
    grouped["category"] = grouped[column].astype(str)
    order = [str(value) for value in sorted(grouped[column].dropna().unique().tolist())]
    fig = px.bar(
        grouped, x="category", y="purchase_rate", category_orders={"category": order},
        title=title, labels={"category": x_label, "purchase_rate": "Purchase rate"},
        hover_data={"customers": ":,", "holders": ":,", "purchase_rate": ":.2%", "category": False},
        color_discrete_sequence=[TEAL],
    )
    fig.add_hline(y=purchase_rate, line_dash="dot", line_color=CORAL, line_width=2)
    fig.update_traces(marker_line_width=0,
                      hovertemplate="Code %{x}<br>Purchase rate %{y:.2%}<br>Customers %{customdata[0]:,}<br>Policyholders %{customdata[1]:,}<extra></extra>")
    fig.update_layout(showlegend=False)
    fig.update_xaxes(type="category")
    return polish_chart(fig, percent_axis=True)


def count_chart(column, title, x_label):
    grouped = filtered.groupby([column, "Caravan status"], observed=True).size().reset_index(name="customers")
    grouped["category"] = grouped[column].astype(str)
    order = [str(value) for value in sorted(filtered[column].dropna().unique().tolist())]
    if column == "Other policy group":
        order = [value for value in ["0", "1", "2–3", "4+"] if value in order]
    fig = px.bar(
        grouped, x="category", y="customers", color="Caravan status", barmode="group",
        category_orders={"category": order, "Caravan status": ["No caravan policy", "Has caravan policy"]},
        color_discrete_map={"Has caravan policy": TEAL, "No caravan policy": "#C9D5E0"},
        title=title, labels={"category": x_label, "customers": "Customers"},
    )
    fig.update_traces(marker_line_width=0, hovertemplate="%{x}<br>%{fullData.name}: %{y:,} customers<extra></extra>")
    fig.update_xaxes(type="category")
    return polish_chart(fig)


def chart_panel(fig):
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


st.markdown('<div class="section-label">Purchase patterns</div>', unsafe_allow_html=True)
st.caption("Purchase-rate charts use all customers in the selected code ranges, regardless of policy status. The status dropdown filters the two customer-count charts. Hover over a rate bar for its exact rate and customer count; the dotted coral line is the cohort average.")
left, right = st.columns(2)
with left:
    chart_panel(rate_chart("MGEMLEEF", "Purchase rate by area age profile", "Area age category (code)"))
    chart_panel(rate_chart("MINKGEM", "Purchase rate by area income profile", "Area income category (code)"))
    chart_panel(count_chart("Other policy group", "Purchase status by existing product portfolio", "Other product policies per customer"))
with right:
    chart_panel(rate_chart("MAUT0", "Purchase rate by area vehicle profile", "Area vehicle category (code)"))
    chart_panel(rate_chart("MRELGE", "Purchase rate by area relationship profile", "Area relationship category (code)"))
    chart_panel(count_chart("MOSHOOFD", "Customer counts by main customer type", "Main customer type (code)"))

st.markdown('<div class="section-label">Key insights in this selection</div>', unsafe_allow_html=True)
age_rates = profile_filtered.groupby("MGEMLEEF", observed=True)["CARAVAN"].agg(["mean", "size"])
income_rates = profile_filtered.groupby("MINKGEM", observed=True)["CARAVAN"].agg(["mean", "size"])
ins1, ins2, ins3 = st.columns(3)
if len(age_rates):
    top_age_code = age_rates["mean"].idxmax()
    top_age_rate = age_rates.loc[top_age_code, "mean"]
    top_age_n = int(age_rates.loc[top_age_code, "size"])
    age_text = f"Area age code {top_age_code}: {top_age_rate:.2%} ({top_age_n:,} customers)"
else:
    age_text = "No age-profile data in this selection"
if len(income_rates):
    top_income_code = income_rates["mean"].idxmax()
    top_income_rate = income_rates.loc[top_income_code, "mean"]
    top_income_n = int(income_rates.loc[top_income_code, "size"])
    income_text = f"Area income code {top_income_code}: {top_income_rate:.2%} ({top_income_n:,} customers)"
else:
    income_text = "No income-profile data in this selection"
with ins1:
    st.markdown(f'<div class="insight-card"><div class="insight-label">Highest area age-code rate</div><div class="insight-value">{age_text}</div></div>', unsafe_allow_html=True)
with ins2:
    st.markdown(f'<div class="insight-card"><div class="insight-label">Highest area income-code rate</div><div class="insight-value">{income_text}</div></div>', unsafe_allow_html=True)
with ins3:
    st.markdown(f'<div class="insight-card"><div class="insight-label">Current code-range cohort</div><div class="insight-value">{n_holders:,} of {n_customers:,} customers ({purchase_rate:.2%})</div></div>', unsafe_allow_html=True)

st.caption("Insights are calculated from the filtered rows. Category codes are shown as codes because they are not exact ages or income amounts.")
with st.expander("About the data and calculations"):
    st.write(
        "This dashboard uses the CoIL 2000 insurance benchmark training records. CARAVAN indicates whether a record has a caravan policy. "
        "The demographic and vehicle profile fields are coded customer-area categories. The dataset has no policy start date or tenure field, "
        "so the dashboard reports existing product portfolio instead. Average other product policies is calculated by summing available A* product-count columns and excluding CARAVAN."
    )



