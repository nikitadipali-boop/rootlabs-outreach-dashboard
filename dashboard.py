"""
RootLabs Outreach Intelligence Dashboard
=========================================
Run with:
    streamlit run dashboard.py

Then open http://localhost:8501 in your browser.
"""

import os
import json
import csv
import time
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Config ────────────────────────────────────────────────────────────────────

try:
    TOKEN = st.secrets["AIRTABLE_TOKEN"]
except Exception:
    TOKEN = "pat0aSErPoCgOSR2B.4bde5ea5bcf124ac0680d144183be4baf5d158be0d19777e8a4fc7dd43037fa8"

BASE_ID  = "appnhGIoeLSfLf9ah"
TABLE_ID = "tblwZwNeuZwtIavqj"
AT_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_DIR   = os.path.join(BASE_DIR, "snapshots")
CHANGELOG_PATH = os.path.join(BASE_DIR, "changelog.csv")

NON_CREATOR_DOMAINS = {
    "periskope.app","accounts.google.com","apollo.io","mail.apollo.io","mail.anthropic.com",
    "tello.com","github.com","airtable.com","mail.airtable.com","engage.canva.com",
    "twelvelabs.io","notify.railway.app","news.railway.app","supabase.com","gamma.app",
    "apify.com","email.openai.com","tm.openai.com","email.claude.com","mail.respond.io",
    "reply.io","fyxer.com","mermaidchart.com","mermaid.ai","team.twilio.com","vidyard.com",
    "superagent.com","info.n8n.io","useloom.com","amazon.com","amazonaws.com",
    "lemlist-news.com","notifications.hubspot.com","mailchimp.com","send.zapier.com",
    "discord.com","reacherapp.com","klaviyo.com","boxbe.com","google.com",
    "successgncapital.com","qualfon.com","goshipcentrlpro.com","ibramdawwa-gmbh.com",
    "partnerssalesbytomorrowlead.info","huntdmfirm.info","evolvedcommerceflows.info",
    "meetapprovalprocessesdigital.com","geniusecommerce-today.com","checkaxisbrands.org",
}

INBOXES = [
    "may_k@rootlabs.co", "may.k@rootlabs.co", "founder@rootlabs.co",
    "may.kumar@rootlabs.co", "mayank.k@rootlabs.co", "mayank.kumar@rootlabs.co",
    "may@rootlabs.co", "ceo@rootlabs.co", "mayk@rootlabs.co",
]

STATUS_COLOURS = {
    "needs_reply":       "#E74C3C",
    "needs_followup_1":  "#F39C12",
    "needs_followup_2":  "#3498DB",
    "needs_followup_3":  "#9B59B6",
    "abandoned":         "#95A5A6",
}

EVENT_COLOURS = {
    "new_inbound":     "#F39C12",
    "replied":         "#27AE60",
    "followup_1_sent": "#3498DB",
    "followup_2_sent": "#9B59B6",
    "followup_3_sent": "#E74C3C",
}

EVENT_LABELS = {
    "new_inbound":     "New Inbounds",
    "replied":         "Replies Sent",
    "followup_1_sent": "Followup 1 Sent",
    "followup_2_sent": "Followup 2 Sent",
    "followup_3_sent": "Followup 3 Sent",
}

# ── Data loaders ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_latest_snapshot():
    files = sorted([
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.startswith("snapshot_") and f.endswith(".json")
    ], reverse=True)
    if not files:
        return {}, "No snapshot found"
    path = os.path.join(SNAPSHOT_DIR, files[0])
    with open(path) as f:
        data = json.load(f)
    date_str = files[0].replace("snapshot_", "").replace(".json", "")
    return data, date_str


@st.cache_data(ttl=300)
def load_all_snapshots():
    """Load all snapshots and return a dict of {date: snapshot}."""
    files = sorted([
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.startswith("snapshot_") and f.endswith(".json")
    ])
    all_snaps = {}
    for fname in files:
        date_str = fname.replace("snapshot_", "").replace(".json", "")
        with open(os.path.join(SNAPSHOT_DIR, fname)) as f:
            all_snaps[date_str] = json.load(f)
    return all_snaps


@st.cache_data(ttl=300)
def load_changelog():
    if not os.path.exists(CHANGELOG_PATH):
        return pd.DataFrame()
    df = pd.read_csv(CHANGELOG_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df


def pull_fresh_snapshot():
    """Pull live data from Airtable and save a new snapshot."""
    all_records = []
    offset = None
    while True:
        params = {"pageSize": 100}
        if offset:
            params["offset"] = offset
        resp = requests.get(
            f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}",
            headers=AT_HEADERS, params=params
        )
        data = resp.json()
        all_records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        time.sleep(0.3)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = {}
    for r in all_records:
        f = r["fields"]
        email = (f.get("creator_email") or "").strip()
        domain = email.split("@")[-1].lower() if "@" in email else ""
        if domain in NON_CREATOR_DOMAINS:
            continue
        if (f.get("action_status_manual") or "") == "needs_no_action":
            continue
        snapshot[r["id"]] = {
            "record_id":           r["id"],
            "creator_email":       email,
            "rootlabs_inbox":      (f.get("rootlabs_email") or "").strip(),
            "thread_status":       (f.get("thread_status") or "").strip(),
            "action_status_final": (f.get("action_status_final") or "").strip(),
            "last_message_type":   (f.get("last_message_type") or "").strip(),
            "last_message_date":   (f.get("last_message_date") or "")[:19],
            "date_of_first_reply": (f.get("date_of_first_reply") or "")[:10],
            "snapshot_date":       today,
        }

    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    snap_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{today}.json")
    with open(snap_path, "w") as fh:
        json.dump(snapshot, fh, indent=2)
    return snapshot, today


# ── Page setup ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RootLabs Outreach Intelligence",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-number { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .metric-label  { font-size: 0.85rem; color: #666; margin-top: 4px; }
    .section-header {
        font-size: 1.1rem; font-weight: 600;
        border-bottom: 2px solid #2F5496;
        padding-bottom: 6px; margin-bottom: 16px;
        color: #2F5496;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/email.png", width=60)
    st.title("Outreach Intelligence")
    st.caption("RootLabs Creator Outreach Tracker")
    st.divider()

    if st.button("🔄  Refresh from Airtable", use_container_width=True):
        with st.spinner("Pulling latest data from Airtable..."):
            pull_fresh_snapshot()
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()

    st.divider()
    page = st.radio(
        "View",
        ["📊  Queue Overview", "📈  Trends & Execution", "📋  Changelog", "🔍  Inbox Drill-Down"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"Data dir: `airtable-visibility-tracker/`")

# ── Load data ─────────────────────────────────────────────────────────────────

snapshot, snap_date = load_latest_snapshot()
changelog_df        = load_changelog()
all_snaps           = load_all_snapshots()

if not snapshot:
    st.error("No snapshot found. Click 'Refresh from Airtable' to load data.")
    st.stop()

snap_df = pd.DataFrame(snapshot.values())
snap_df = snap_df[snap_df["thread_status"].isin([
    "needs_reply", "needs_followup_1", "needs_followup_2", "needs_followup_3", "abandoned"
])]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: Queue Overview
# ══════════════════════════════════════════════════════════════════════════════

if page == "📊  Queue Overview":
    st.title("📬 Queue Overview")
    st.caption(f"Snapshot date: **{snap_date}**  ·  {len(snap_df):,} active creator threads")
    st.divider()

    # Top-level KPI metrics
    nr   = len(snap_df[snap_df["thread_status"] == "needs_reply"])
    nf1  = len(snap_df[snap_df["thread_status"] == "needs_followup_1"])
    nf2  = len(snap_df[snap_df["thread_status"] == "needs_followup_2"])
    nf3  = len(snap_df[snap_df["thread_status"] == "needs_followup_3"])
    total = nr + nf1 + nf2 + nf3

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, colour in [
        (c1, "Needs Reply",      nr,    "#E74C3C"),
        (c2, "Needs Followup 1", nf1,   "#F39C12"),
        (c3, "Needs Followup 2", nf2,   "#3498DB"),
        (c4, "Needs Followup 3", nf3,   "#9B59B6"),
        (c5, "Total Active",     total, "#2F5496"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <p class="metric-number" style="color:{colour}">{val}</p>
            <p class="metric-label">{label}</p>
        </div>""", unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown('<p class="section-header">Queue by Inbox</p>', unsafe_allow_html=True)

        inbox_data = []
        for inbox in INBOXES:
            idf = snap_df[snap_df["rootlabs_inbox"] == inbox]
            inbox_data.append({
                "Inbox": inbox.replace("@rootlabs.co", ""),
                "Needs Reply":      len(idf[idf["thread_status"] == "needs_reply"]),
                "Needs Followup 1": len(idf[idf["thread_status"] == "needs_followup_1"]),
                "Needs Followup 2": len(idf[idf["thread_status"] == "needs_followup_2"]),
                "Needs Followup 3": len(idf[idf["thread_status"] == "needs_followup_3"]),
            })
        inbox_df = pd.DataFrame(inbox_data)
        inbox_df["Total"] = inbox_df[["Needs Reply","Needs Followup 1","Needs Followup 2","Needs Followup 3"]].sum(axis=1)
        inbox_df = inbox_df[inbox_df["Total"] > 0].sort_values("Total", ascending=False)

        fig_bar = px.bar(
            inbox_df.melt(id_vars="Inbox", value_vars=["Needs Reply","Needs Followup 1","Needs Followup 2","Needs Followup 3"]),
            x="value", y="Inbox", color="variable", orientation="h",
            color_discrete_map={
                "Needs Reply":      "#E74C3C",
                "Needs Followup 1": "#F39C12",
                "Needs Followup 2": "#3498DB",
                "Needs Followup 3": "#9B59B6",
            },
            labels={"value": "Threads", "variable": "Status"},
        )
        fig_bar.update_layout(
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown('<p class="section-header">Status Distribution</p>', unsafe_allow_html=True)

        status_counts = snap_df["thread_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        status_label_map = {
            "needs_reply":      "Needs Reply",
            "needs_followup_1": "Needs Followup 1",
            "needs_followup_2": "Needs Followup 2",
            "needs_followup_3": "Needs Followup 3",
            "abandoned":        "Abandoned",
        }
        status_counts["Label"] = status_counts["Status"].map(status_label_map).fillna(status_counts["Status"])
        colour_list = [STATUS_COLOURS.get(s, "#ccc") for s in status_counts["Status"]]

        fig_pie = px.pie(
            status_counts, values="Count", names="Label",
            color="Status",
            color_discrete_map=STATUS_COLOURS,
            hole=0.45,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False, paper_bgcolor="white",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Inbox summary table
    st.markdown('<p class="section-header">Inbox Breakdown Table</p>', unsafe_allow_html=True)
    display_df = inbox_df.copy()
    display_df["Inbox"] = display_df["Inbox"] + "@rootlabs.co"
    st.dataframe(
        display_df.set_index("Inbox"),
        use_container_width=True,
        height=320,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: Trends & Execution
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📈  Trends & Execution":
    st.title("📈 Trends & Execution Rate")
    st.divider()

    if changelog_df.empty:
        st.info("No changelog data yet. Run `daily_tracker.py` daily to build history.")
        st.stop()

    # ── Queue depth over time (from snapshots) ────────────────────────────────
    st.markdown('<p class="section-header">Queue Depth Over Time</p>', unsafe_allow_html=True)

    if len(all_snaps) > 1:
        trend_rows = []
        for date_str, snap in sorted(all_snaps.items()):
            recs = list(snap.values())
            trend_rows.append({
                "Date": pd.to_datetime(date_str),
                "Needs Reply":      sum(1 for r in recs if r["thread_status"] == "needs_reply"),
                "Needs Followup 1": sum(1 for r in recs if r["thread_status"] == "needs_followup_1"),
                "Needs Followup 2": sum(1 for r in recs if r["thread_status"] == "needs_followup_2"),
                "Needs Followup 3": sum(1 for r in recs if r["thread_status"] == "needs_followup_3"),
            })
        trend_df = pd.DataFrame(trend_rows)

        fig_trend = px.line(
            trend_df.melt(id_vars="Date", var_name="Status", value_name="Count"),
            x="Date", y="Count", color="Status",
            color_discrete_map={
                "Needs Reply":      "#E74C3C",
                "Needs Followup 1": "#F39C12",
                "Needs Followup 2": "#3498DB",
                "Needs Followup 3": "#9B59B6",
            },
            markers=True,
        )
        fig_trend.update_layout(
            height=340, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Queue trend will appear here once you have 2+ days of snapshots.")

    st.divider()

    # ── Daily execution (from changelog) ─────────────────────────────────────
    st.markdown('<p class="section-header">Daily Execution - What Got Actioned</p>', unsafe_allow_html=True)

    # Filter out baseline new_inbound entries (first run populates everything as new_inbound)
    exec_df = changelog_df[changelog_df["event_type"] != "new_inbound"].copy()

    if exec_df.empty:
        st.info("Execution data will appear here once the team starts actioning threads.")
    else:
        daily_exec = exec_df.groupby(["date", "event_type"]).size().reset_index(name="count")
        daily_exec["label"] = daily_exec["event_type"].map(EVENT_LABELS).fillna(daily_exec["event_type"])

        fig_exec = px.bar(
            daily_exec, x="date", y="count", color="event_type",
            color_discrete_map=EVENT_COLOURS,
            labels={"count": "Actions", "date": "Date", "event_type": "Action Type"},
            barmode="group",
        )
        fig_exec.update_layout(
            height=340, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        st.plotly_chart(fig_exec, use_container_width=True)

    st.divider()

    # ── New inbounds over time ────────────────────────────────────────────────
    st.markdown('<p class="section-header">New Inbounds Per Day</p>', unsafe_allow_html=True)

    inbound_df = changelog_df[changelog_df["event_type"] == "new_inbound"].copy()
    # Exclude the baseline run (day 1 will have 1000+ entries - filter those out)
    inbound_by_day = inbound_df.groupby("date").size().reset_index(name="count")
    inbound_by_day = inbound_by_day[inbound_by_day["count"] < 500]  # filter baseline spike

    if inbound_by_day.empty:
        st.info("New inbound trends will appear here after the first day of live tracking.")
    else:
        fig_inb = px.bar(
            inbound_by_day, x="date", y="count",
            labels={"count": "New Inbounds", "date": "Date"},
            color_discrete_sequence=["#F39C12"],
        )
        fig_inb.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_inb, use_container_width=True)

    st.divider()

    # ── Execution rate ────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Execution Rate by Inbox</p>', unsafe_allow_html=True)

    if not exec_df.empty:
        exec_by_inbox = exec_df.groupby(["rootlabs_inbox", "event_type"]).size().unstack(fill_value=0).reset_index()
        exec_by_inbox.columns.name = None
        exec_by_inbox["Inbox"] = exec_by_inbox["rootlabs_inbox"].str.replace("@rootlabs.co","")
        st.dataframe(exec_by_inbox.drop(columns=["rootlabs_inbox"]).set_index("Inbox"),
                     use_container_width=True)
    else:
        st.info("Execution breakdown by inbox will appear here once threads are actioned.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: Changelog
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋  Changelog":
    st.title("📋 Full Changelog")
    st.caption("Every state transition detected across all creator threads.")
    st.divider()

    if changelog_df.empty:
        st.info("No changelog entries yet.")
        st.stop()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        event_filter = st.multiselect(
            "Event Type",
            options=list(EVENT_LABELS.values()),
            default=list(EVENT_LABELS.values()),
        )
    with col2:
        inbox_filter = st.multiselect(
            "Inbox",
            options=INBOXES,
            default=INBOXES,
        )
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(changelog_df["date"].min(), changelog_df["date"].max()),
        )

    label_to_event = {v: k for k, v in EVENT_LABELS.items()}
    selected_events = [label_to_event.get(e, e) for e in event_filter]

    filtered = changelog_df[
        (changelog_df["event_type"].isin(selected_events)) &
        (changelog_df["rootlabs_inbox"].isin(inbox_filter))
    ]
    if len(date_range) == 2:
        filtered = filtered[
            (filtered["date"] >= pd.to_datetime(date_range[0])) &
            (filtered["date"] <= pd.to_datetime(date_range[1]))
        ]

    filtered = filtered.sort_values("detected_at", ascending=False).copy()
    filtered["event_type"] = filtered["event_type"].map(EVENT_LABELS).fillna(filtered["event_type"])

    st.caption(f"Showing {len(filtered):,} of {len(changelog_df):,} entries")

    st.dataframe(
        filtered[[
            "date", "event_type", "creator_email",
            "rootlabs_inbox", "from_status", "to_status", "last_message_date"
        ]].rename(columns={
            "date": "Date",
            "event_type": "Event",
            "creator_email": "Creator Email",
            "rootlabs_inbox": "Inbox",
            "from_status": "From",
            "to_status": "To",
            "last_message_date": "Last Message",
        }),
        use_container_width=True,
        height=520,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: Inbox Drill-Down
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔍  Inbox Drill-Down":
    st.title("🔍 Inbox Drill-Down")
    st.divider()

    selected_inbox = st.selectbox("Select inbox", INBOXES)

    inbox_snap = snap_df[snap_df["rootlabs_inbox"] == selected_inbox].copy()

    if inbox_snap.empty:
        st.info(f"No active threads for {selected_inbox}")
        st.stop()

    # KPIs for this inbox
    nr  = len(inbox_snap[inbox_snap["thread_status"] == "needs_reply"])
    nf1 = len(inbox_snap[inbox_snap["thread_status"] == "needs_followup_1"])
    nf2 = len(inbox_snap[inbox_snap["thread_status"] == "needs_followup_2"])
    nf3 = len(inbox_snap[inbox_snap["thread_status"] == "needs_followup_3"])

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, colour in [
        (c1, "Needs Reply",      nr,  "#E74C3C"),
        (c2, "Needs Followup 1", nf1, "#F39C12"),
        (c3, "Needs Followup 2", nf2, "#3498DB"),
        (c4, "Needs Followup 3", nf3, "#9B59B6"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <p class="metric-number" style="color:{colour}">{val}</p>
            <p class="metric-label">{label}</p>
        </div>""", unsafe_allow_html=True)

    st.divider()

    status_filter = st.multiselect(
        "Filter by status",
        options=["needs_reply","needs_followup_1","needs_followup_2","needs_followup_3"],
        default=["needs_reply","needs_followup_1","needs_followup_2","needs_followup_3"],
    )

    filtered_inbox = inbox_snap[inbox_snap["thread_status"].isin(status_filter)].copy()
    filtered_inbox["last_message_date"] = filtered_inbox["last_message_date"].str[:10]
    filtered_inbox = filtered_inbox.sort_values("last_message_date")

    st.caption(f"{len(filtered_inbox)} threads")
    st.dataframe(
        filtered_inbox[[
            "creator_email", "thread_status", "action_status_final",
            "last_message_type", "last_message_date", "date_of_first_reply"
        ]].rename(columns={
            "creator_email":      "Creator Email",
            "thread_status":      "Status",
            "action_status_final":"Last Action",
            "last_message_type":  "Last Msg Type",
            "last_message_date":  "Last Msg Date",
            "date_of_first_reply":"First Reply Date",
        }),
        use_container_width=True,
        height=480,
    )

    # Changelog for this inbox
    if not changelog_df.empty:
        st.divider()
        st.markdown(f'<p class="section-header">Changelog for {selected_inbox}</p>', unsafe_allow_html=True)
        inbox_log = changelog_df[changelog_df["rootlabs_inbox"] == selected_inbox].copy()
        inbox_log = inbox_log.sort_values("detected_at", ascending=False)
        inbox_log["event_type"] = inbox_log["event_type"].map(EVENT_LABELS).fillna(inbox_log["event_type"])
        st.dataframe(
            inbox_log[["date","event_type","creator_email","from_status","to_status"]].rename(columns={
                "date": "Date", "event_type": "Event",
                "creator_email": "Creator", "from_status": "From", "to_status": "To",
            }),
            use_container_width=True,
            height=280,
        )
