import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Playwright scraper ─────────────────────────────────────────────────────────
def scrape_data():
    try:
        from playwright.sync_api import sync_playwright

        records = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://poshanabhiyaan.gov.in/", timeout=60000)

            # Wait for state cards to appear
            page.wait_for_selector(".ja_dash_new_activity_reported_state_name", timeout=30000)
            page.wait_for_timeout(3000)  # allow full JS render

            state_names = page.query_selector_all(".ja_dash_new_activity_reported_state_name")
            total_dists = page.query_selector_all(".ja_dash_new_activity_reported_total_dist_count")
            part_dists  = page.query_selector_all(".ja_dash_new_activity_dist_partici_count")
            activities  = page.query_selector_all(".ja_dash_new_activity_count")

            for i in range(len(state_names)):
                name = state_names[i].inner_text().strip()
                if name.upper() == "TOTAL":
                    continue
                try:
                    records.append({
                        "state":           name,
                        "total_districts": int(total_dists[i].inner_text().strip().replace(",", "")),
                        "participating":   int(part_dists[i].inner_text().strip().replace(",", "")),
                        "activities":      int(activities[i].inner_text().strip().replace(",", "")),
                    })
                except Exception:
                    continue

            browser.close()

        if not records:
            return None, "No data found on page. Website structure may have changed."

        return records, None

    except ImportError:
        return None, "playwright_not_installed"
    except Exception as e:
        return None, str(e)


# ── Fallback hardcoded data ────────────────────────────────────────────────────
FALLBACK_DATA = [
    {"state": "Andaman & Nicobar Islands",          "total_districts": 3,  "participating": 3,  "activities": 145},
    {"state": "Andhra Pradesh",                      "total_districts": 28, "participating": 27, "activities": 294740},
    {"state": "Arunachal Pradesh",                   "total_districts": 27, "participating": 12, "activities": 154},
    {"state": "Assam",                               "total_districts": 35, "participating": 5,  "activities": 9},
    {"state": "Bihar",                               "total_districts": 38, "participating": 38, "activities": 389151},
    {"state": "Chhattisgarh",                        "total_districts": 33, "participating": 33, "activities": 220715},
    {"state": "Dadra & Nagar Haveli - Daman & Diu", "total_districts": 3,  "participating": 3,  "activities": 239},
    {"state": "Delhi",                               "total_districts": 11, "participating": 11, "activities": 2803},
    {"state": "Goa",                                 "total_districts": 2,  "participating": 2,  "activities": 154},
    {"state": "Gujarat",                             "total_districts": 33, "participating": 33, "activities": 113772},
    {"state": "Haryana",                             "total_districts": 22, "participating": 22, "activities": 25120},
    {"state": "Himachal Pradesh",                    "total_districts": 12, "participating": 12, "activities": 5345},
    {"state": "J&K",                                 "total_districts": 20, "participating": 20, "activities": 37788},
    {"state": "Jharkhand",                           "total_districts": 24, "participating": 24, "activities": 54201},
    {"state": "Karnataka",                           "total_districts": 31, "participating": 30, "activities": 21841},
    {"state": "Kerala",                              "total_districts": 14, "participating": 14, "activities": 6185},
    {"state": "Ladakh",                              "total_districts": 2,  "participating": 2,  "activities": 7},
    {"state": "Lakshadweep",                         "total_districts": 1,  "participating": 0,  "activities": 0},
    {"state": "Madhya Pradesh",                      "total_districts": 55, "participating": 55, "activities": 337234},
    {"state": "Maharashtra",                         "total_districts": 36, "participating": 36, "activities": 356005},
    {"state": "Manipur",                             "total_districts": 16, "participating": 7,  "activities": 604},
    {"state": "Meghalaya",                           "total_districts": 12, "participating": 4,  "activities": 24},
    {"state": "Mizoram",                             "total_districts": 11, "participating": 5,  "activities": 83},
    {"state": "Nagaland",                            "total_districts": 17, "participating": 13, "activities": 129},
    {"state": "Odisha",                              "total_districts": 30, "participating": 30, "activities": 114557},
    {"state": "Puducherry",                          "total_districts": 4,  "participating": 0,  "activities": 0},
    {"state": "Punjab",                              "total_districts": 23, "participating": 23, "activities": 85419},
    {"state": "Rajasthan",                           "total_districts": 41, "participating": 41, "activities": 338663},
    {"state": "Sikkim",                              "total_districts": 6,  "participating": 4,  "activities": 134},
    {"state": "Tamil Nadu",                          "total_districts": 38, "participating": 34, "activities": 63298},
    {"state": "Telangana",                           "total_districts": 33, "participating": 33, "activities": 78427},
    {"state": "Tripura",                             "total_districts": 8,  "participating": 5,  "activities": 37},
    {"state": "UT-Chandigarh",                       "total_districts": 1,  "participating": 1,  "activities": 2125},
    {"state": "Uttar Pradesh",                       "total_districts": 75, "participating": 74, "activities": 72801},
    {"state": "Uttarakhand",                         "total_districts": 13, "participating": 11, "activities": 1078},
    {"state": "West Bengal",                         "total_districts": 23, "participating": 4,  "activities": 5},
]


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poshan Abhiyaan Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1a5c38; padding-bottom: 0.25rem; }
    .sub-header  { font-size: 0.9rem; color: #666; margin-bottom: 1.25rem; }
    .section-title {
        font-size: 1.05rem; font-weight: 600; color: #1a5c38;
        margin: 1rem 0 0.4rem;
        border-bottom: 2px solid #a5d6a7; padding-bottom: 4px;
    }
    div[data-testid="metric-container"] {
        background: #f8fdf9; border: 1px solid #c8e6c9;
        border-radius: 10px; padding: 12px 16px;
    }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session-state cache ────────────────────────────────────────────────────────
if "data"         not in st.session_state: st.session_state.data         = None
if "last_fetched" not in st.session_state: st.session_state.last_fetched = None
if "data_source"  not in st.session_state: st.session_state.data_source  = None
if "error_msg"    not in st.session_state: st.session_state.error_msg    = None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 Poshan Abhiyaan")
    st.markdown("[poshanabhiyaan.gov.in](https://poshanabhiyaan.gov.in/)")
    st.markdown("---")

    if st.session_state.last_fetched:
        st.success(f"✅ Source: **{st.session_state.data_source}**")
        st.caption(f"Last fetched: {st.session_state.last_fetched}")
    else:
        st.info("Click 'Fetch Live' to load latest data.")

    col_a, col_b = st.columns(2)
    fetch_live   = col_a.button("🌐 Fetch Live",  use_container_width=True)
    use_fallback = col_b.button("📦 Use Saved",   use_container_width=True)

    st.markdown("---")
    st.markdown("### Filters")
    act_range      = st.slider("Min activities",        0, 400000, 0, step=1000)
    part_threshold = st.slider("Min participation (%)", 0, 100,    0, step=5)
    chart_type     = st.radio("Chart style", ["Horizontal bar", "Treemap", "Scatter"], index=0)

    st.markdown("---")
    if st.session_state.error_msg:
        st.error(f"⚠️ {st.session_state.error_msg}")


# ── Fetch logic ────────────────────────────────────────────────────────────────
if fetch_live:
    with st.spinner("🌐 Scraping live data … this may take ~30 seconds"):
        records, err = scrape_data()

    if err == "playwright_not_installed":
        st.session_state.error_msg = (
            "Playwright not installed. Run these two commands:\n"
            "pip install playwright\n"
            "playwright install chromium"
        )
        st.session_state.data        = FALLBACK_DATA
        st.session_state.data_source = "Saved (fallback — Playwright missing)"
        st.session_state.last_fetched = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    elif err:
        st.session_state.error_msg   = f"Scraping failed: {err}. Showing saved data."
        st.session_state.data        = FALLBACK_DATA
        st.session_state.data_source = "Saved (fallback)"
        st.session_state.last_fetched = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    else:
        st.session_state.error_msg   = None
        st.session_state.data        = records
        st.session_state.data_source = "Live — poshanabhiyaan.gov.in"
        st.session_state.last_fetched = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        st.success("✅ Live data fetched successfully!")

if use_fallback:
    st.session_state.data        = FALLBACK_DATA
    st.session_state.data_source = "Saved data"
    st.session_state.last_fetched = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    st.session_state.error_msg   = None

# Auto-load saved data on first run
if st.session_state.data is None:
    st.session_state.data        = FALLBACK_DATA
    st.session_state.data_source = "Saved data (auto-loaded)"
    st.session_state.last_fetched = datetime.now().strftime("%d %b %Y, %H:%M:%S")


# ── Build dataframe ────────────────────────────────────────────────────────────
df = pd.DataFrame(st.session_state.data)
df["participation_rate"]    = (df["participating"] / df["total_districts"].replace(0, 1) * 100).round(1)
df["activity_per_district"] = (df["activities"] / df["participating"].replace(0, 1)).round(0).astype(int)

TOTAL_DISTRICTS  = int(df["total_districts"].sum())
TOTAL_PARTICI    = int(df["participating"].sum())
TOTAL_ACTIVITIES = int(df["activities"].sum())
PARTICI_RATE     = round(TOTAL_PARTICI / TOTAL_DISTRICTS * 100, 1)

filtered = df[
    (df["activities"] >= act_range) &
    (df["participation_rate"] >= part_threshold)
].copy()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🌿 Poshan Abhiyaan — Activity Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Jan Andolan activities reported across States & UTs &nbsp;|&nbsp; '
    f'Source: <b>{st.session_state.data_source}</b> &nbsp;|&nbsp; '
    f'Last updated: <b>{st.session_state.last_fetched}</b></div>',
    unsafe_allow_html=True
)

# ── KPI cards ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Districts",         f"{TOTAL_DISTRICTS:,}")
k2.metric("Districts Participating", f"{TOTAL_PARTICI:,}", f"{PARTICI_RATE}% coverage")
k3.metric("Total Activities",        f"{TOTAL_ACTIVITIES:,.0f}")
k4.metric("States / UTs shown",      f"{len(filtered)} / {len(df)}")

st.markdown("---")

# ── Main chart + table ─────────────────────────────────────────────────────────
col_chart, col_table = st.columns([3, 2], gap="medium")

with col_chart:
    st.markdown('<div class="section-title">Activities by State / UT</div>', unsafe_allow_html=True)
    top_n = filtered.sort_values("activities", ascending=False).head(20)

    if chart_type == "Horizontal bar":
        fig = px.bar(
            top_n.sort_values("activities"),
            x="activities", y="state", orientation="h",
            color="participation_rate",
            color_continuous_scale=["#c8e6c9", "#1b5e20"],
            labels={"activities": "Total Activities", "state": "", "participation_rate": "Part. %"},
            hover_data={"participating": True, "total_districts": True}
        )
        fig.update_layout(
            height=520, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Part. %", thickness=12),
            margin=dict(l=0, r=10, t=10, b=30),
            xaxis=dict(gridcolor="#e8f5e9"),
        )
    elif chart_type == "Treemap":
        fig = px.treemap(
            filtered[filtered["activities"] > 0],
            path=["state"], values="activities",
            color="participation_rate",
            color_continuous_scale=["#c8e6c9", "#1b5e20"],
            hover_data={"participating": True, "total_districts": True}
        )
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
    else:
        fig = px.scatter(
            filtered, x="total_districts", y="activities",
            size="participating", color="participation_rate",
            color_continuous_scale=["#c8e6c9", "#1b5e20"],
            hover_name="state",
            labels={"total_districts": "Total Districts", "activities": "Total Activities",
                    "participating": "Districts Participating", "participation_rate": "Part. %"},
            size_max=40
        )
        fig.update_layout(
            height=520, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#e8f5e9"), yaxis=dict(gridcolor="#e8f5e9"),
        )

    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.markdown('<div class="section-title">State-wise Summary</div>', unsafe_allow_html=True)
    display_df = filtered[["state", "total_districts", "participating", "participation_rate", "activities"]].copy()
    display_df.columns = ["State", "Total Dist.", "Participating", "Part. %", "Activities"]
    display_df = display_df.sort_values("Activities", ascending=False).reset_index(drop=True)
    display_df["Activities"] = display_df["Activities"].map("{:,}".format)
    st.dataframe(display_df, use_container_width=True, height=520, hide_index=True)

# ── Bottom row ─────────────────────────────────────────────────────────────────
st.markdown("---")
b1, b2 = st.columns(2, gap="medium")

with b1:
    st.markdown('<div class="section-title">Participation Rate — Top 15 States</div>', unsafe_allow_html=True)
    part_df = filtered.sort_values("participation_rate", ascending=False).head(15)
    fig2 = go.Figure(go.Bar(
        x=part_df["state"], y=part_df["participation_rate"],
        marker_color="#2e7d52",
        text=part_df["participation_rate"].astype(str) + "%",
        textposition="outside"
    ))
    fig2.update_layout(
        height=340, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 115], gridcolor="#e8f5e9", title=""),
        xaxis=dict(tickangle=-35, title=""),
        margin=dict(l=0, r=0, t=10, b=80)
    )
    st.plotly_chart(fig2, use_container_width=True)

with b2:
    st.markdown('<div class="section-title">Activity Distribution</div>', unsafe_allow_html=True)
    bins_df = filtered[filtered["activities"] > 0].copy()
    bins_df["tier"] = pd.cut(
        bins_df["activities"],
        bins=[0, 1000, 10000, 100000, float("inf")],
        labels=["< 1K", "1K – 10K", "10K – 1 Lakh", "> 1 Lakh"]
    )
    tier_counts = bins_df["tier"].value_counts().sort_index()
    fig3 = go.Figure(go.Pie(
        labels=tier_counts.index.tolist(), values=tier_counts.values,
        hole=0.45,
        marker_colors=["#a5d6a7", "#4caf50", "#2e7d52", "#1b5e20"],
        textinfo="label+percent"
    ))
    fig3.update_layout(
        height=340, paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True, margin=dict(l=0, r=0, t=10, b=10)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Low participation alert ────────────────────────────────────────────────────
low = df[(df["participation_rate"] < 50) & (df["total_districts"] > 1)].sort_values("participation_rate")
if len(low) > 0:
    with st.expander(f"⚠️ {len(low)} states with participation rate below 50%"):
        st.dataframe(
            low[["state", "total_districts", "participating", "participation_rate", "activities"]]
              .rename(columns={
                  "state": "State", "total_districts": "Total Dist.",
                  "participating": "Participating", "participation_rate": "Part. %",
                  "activities": "Activities"
              }),
            use_container_width=True, hide_index=True
        )
