import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Authorstats",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Editorial Ledger CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

:root {
    --primary:                #001641;
    --primary-container:      #00296b;
    --primary-fixed:          #dae2ff;
    --primary-fixed-dim:      #b1c5ff;
    --on-primary:             #ffffff;
    --on-primary-fixed-variant: #264486;
    --secondary:              #545e7a;
    --secondary-container:    #d2dcfd;
    --on-secondary-container: #57607c;
    --tertiary:               #340a00;
    --tertiary-container:     #561801;
    --on-tertiary-container:  #d97c5b;
    --tertiary-fixed-dim:     #ffb59c;
    --surface:                #f8f9fa;
    --surface-bright:         #f8f9fa;
    --surface-container-lowest: #ffffff;
    --surface-container-low:  #f3f4f5;
    --surface-container:      #edeeef;
    --surface-container-high: #e7e8e9;
    --surface-container-highest: #e1e3e4;
    --on-surface:             #191c1d;
    --on-surface-variant:     #444650;
    --outline:                #747781;
    --outline-variant:        #c4c6d2;
    --error:                  #ba1a1a;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--surface) !important;
    color: var(--on-surface) !important;
}

/* ปรับสไตล์ปุ่ม Sidebar ให้ชิดซ้ายและรองรับไอคอน */
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent !important;
    border: none !important;
    color: #ffffff !important;
    text-align: left !important;
    justify-content: flex-start !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 10px 15px !important;
    width: 100% !important;
    text-transform: none !important;
}

/* แถบสีไฮไลต์เมื่อเลือก (เหมือนภาพที่ 2) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: #264486 !important; /* สีน้ำเงินสว่าง */
    border-radius: 8px !important;
}

/* ── Topbar / Header ── */
header[data-testid="stHeader"] {
    background: rgba(248, 249, 250, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: none !important;
    box-shadow: 0 1px 0 rgba(0,0,0,0.04) !important;
}

/* ── Hide default streamlit decorations ── */
#MainMenu, footer { display: none !important; }
[data-testid="block-container"] { padding-top: 1.5rem !important; }

/* ── Metric Cards (Bento) ── */
.metric-card {
    background: var(--surface-container-lowest);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    transition: background 0.15s ease;
    box-shadow: 0 2px 8px rgba(0, 22, 65, 0.04);
}
.metric-card:hover { background: var(--surface-container-low); }
.metric-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--on-surface-variant);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--primary);
    line-height: 1;
}
.metric-trend {
    font-size: 11px;
    font-weight: 600;
    margin-top: 0.4rem;
    color: var(--on-surface-variant);
}
.metric-trend.up   { color: #166534; }
.metric-trend.down { color: var(--error); }

/* ── Section Headers ── */
.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--on-surface-variant);
    margin-bottom: 1rem;
}
.page-headline {
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--primary);
    margin-bottom: 0.25rem;
}
.page-sub {
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    margin-bottom: 1.5rem;
}

/* ── Cards / Panels ── */
.panel {
    background: var(--surface-container-lowest);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 22, 65, 0.04);
    margin-bottom: 1rem;
}
.panel-header {
    background: var(--surface-container-low);
    border-radius: 12px 12px 0 0;
    padding: 1rem 1.5rem;
    margin: -1.5rem -1.5rem 1.25rem -1.5rem;
}

/* ── Tables ── */
[data-testid="stDataFrame"] { border: none !important; }
[data-testid="stDataFrame"] table {
    border-collapse: separate !important;
    border-spacing: 0 4px !important;
}
[data-testid="stDataFrame"] th {
    background: var(--surface-container-low) !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--on-surface-variant) !important;
    border: none !important;
    padding: 10px 16px !important;
}
[data-testid="stDataFrame"] td {
    background: var(--surface-container-lowest) !important;
    border: none !important;
    padding: 10px 16px !important;
    font-size: 0.875rem !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: var(--surface-container-low) !important;
}

/* ── Inputs ── */
.stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input {
    background: var(--surface-container-lowest) !important;
    border: 1px solid rgba(196, 198, 210, 0.35) !important;
    border-radius: 8px !important;
    color: var(--on-surface) !important;
    font-size: 0.875rem !important;
    box-shadow: none !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0, 22, 65, 0.08) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-container) 100%) !important;
    color: var(--on-primary) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.8125rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.25rem !important;
    box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.12) !important;
    transition: opacity 0.15s ease, transform 0.1s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"], button.secondary {
    background: var(--surface-container-high) !important;
    color: var(--on-surface) !important;
    box-shadow: none !important;
}

/* ── Status Badges ── */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-published { background: #dcfce7; color: #166534; }
.badge-draft     { background: var(--surface-container-high); color: var(--on-surface-variant); }
.badge-writing   { background: var(--primary-fixed); color: var(--primary); }
.badge-hidden    { background: #fef3c7; color: #92400e; }
.badge-archived  { background: var(--surface-container-highest); color: var(--on-surface-variant); }
.badge-main      { background: var(--secondary-container); color: var(--primary); }
.badge-support   { background: var(--surface-container-high); color: var(--on-surface-variant); }

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--on-surface-variant) !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid rgba(196,198,210,0.25) !important;
    gap: 1.5rem !important;
}

/* ── Dividers as spacing, not lines ── */
hr { border: none !important; margin: 1.5rem 0 !important; }

/* ── Toast-like success messages ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.875rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface-container-high); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─── Supabase Client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def supabase() -> Client:
    return get_supabase()


# ─── Data Fetchers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_stories():
    # ต้องมั่นใจว่ามี .is_("deleted_at", "null") เพื่อให้หน้า Registry ไม่ดึงตัวที่ลบแล้วมา
    res = supabase().table("stories").select("*").is_("deleted_at", "null").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_episodes():
    # ต้องมั่นใจว่าใส่ .is_("deleted_at", "null") เพื่อไม่ให้ดึงรายการที่ลบไปแล้วมาแสดง
    # เพราะถ้าดึงมา แล้วโค้ดข้างล่างพยายามไปอ่าน row['stories']['title'] ของเรื่องที่ถูกลบไปก่อนหน้า อาจจะพังได้
    try:
        res = supabase().table("episodes").select("*, stories(title)").is_("deleted_at", "null").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_characters():
    res = supabase().table("characters").select("*, stories(title)").is_("deleted_at", "null").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_incomes():
    # ต้องมั่นใจว่ามี income_types(income_type_name) อยู่ใน select
    res = supabase().table("incomes").select("*, stories(title), platforms(platform_name), income_types(income_type_name), episodes(episode_number, title)").is_("deleted_at", "null").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_statistics():
    res = supabase().table("statistics").select("*, stories(title), platforms(platform_name)").order("recorded_at", desc=True).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_platforms():
    res = supabase().table("platforms").select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_genres():
    res = supabase().table("genres").select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def fetch_story_genres(story_id):
    # ดึงชื่อประเภทที่ผูกกับเรื่องนี้
    res = supabase().table("story_genres").select("genre_id, genres(genre_name)").eq("story_id", story_id).execute()
    return [item['genres']['genre_name'] for item in res.data] if res.data else []

@st.cache_data(ttl=300)
def fetch_income_types():
    res = supabase().table("income_types").select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# ─── Data Helpers ─────────────────────────────────────────────────────────────
def soft_delete(table_name, id_column, id_value):
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # 1. สั่ง Soft Delete รายการหลัก
    supabase().table(table_name).update({"deleted_at": now}).eq(id_column, id_value).execute()
    
    # 2. กรณีลบ Story ให้สั่งลบ Episodes และ Characters ที่ผูกอยู่ด้วย (Cascading)
    if table_name == "stories":
        # ลบ Episodes ที่ผูกกับ Story นี้
        supabase().table("episodes").update({"deleted_at": now}).eq("story_id", id_value).execute()
        # ลบ Characters ที่ผูกกับ Story นี้
        supabase().table("characters").update({"deleted_at": now}).eq("story_id", id_value).execute()
        # ลบ Incomes ที่ผูกกับ Story นี้ (ถ้ามี column story_id)
        # supabase().table("incomes").update({"deleted_at": now}).eq("story_id", id_value).execute()

    clear_cache()
    st.toast(f"Moved {table_name} to Trash", icon="🗑️")

def restore_item(table_name, id_column, id_value):
    """กู้คืนข้อมูลจากถังขยะ"""
    try:
        supabase().table(table_name).update({"deleted_at": None}).eq(id_column, id_value).execute()
        clear_cache()
        st.toast("Item restored!", icon="♻️")
    except Exception as e:
        st.error(f"Error: {e}")

def fetch_trash(table_name):
    # ปรับให้ดึงข้อมูลความสัมพันธ์มาด้วยตามประเภทตาราง
    if table_name in ["episodes", "characters", "incomes", "statistics"]:
        query = supabase().table(table_name).select("*, stories(title)")
    else:
        query = supabase().table(table_name).select("*")
        
    res = query.not_.is_("deleted_at", "null").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def clear_cache():
    fetch_stories.clear()
    fetch_episodes.clear()
    fetch_characters.clear()
    fetch_incomes.clear()
    fetch_statistics.clear()
    fetch_platforms.clear()
    fetch_genres.clear()
    fetch_income_types.clear()


# ─── Chart Helper ─────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#444650", size=11),
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="rgba(196,198,210,0.15)", zeroline=True,
               zerolinecolor="rgba(196,198,210,0.4)", tickfont=dict(size=10)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10)),
    colorway=["#001641", "#545e7a", "#340a00", "#b1c5ff", "#d97c5b"],
)

def styled_chart(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


# ─── Badge HTML ───────────────────────────────────────────────────────────────
def badge(text, kind="draft"):
    mapping = {
        "Published": "published", "Draft": "draft", "Writing": "writing",
        "Hidden": "hidden", "Archived": "archived",
        "Main": "main", "Support": "support",
    }
    cls = mapping.get(text, "draft")
    return f'<span class="badge badge-{cls}">{text}</span>'


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Authorstats</div>', unsafe_allow_html=True)

    # เปลี่ยน Map ให้ตรงกับชื่อไอคอน Material Symbols
    pages = {
        "Dashboard": "dashboard",
        "Analytics":   "analytics",
        "Stories": "description",
        "Episodes": "menu_book",
        "Characters": "person",
        "Revenue": "payments",
        "Statistics": "analytics",
        "Settings": "settings",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    for label, icon in pages.items():
        active = st.session_state.page == label
        
        # ใส่ไอคอน Material Symbols เข้าไปใน Label ของปุ่ม
        btn_label = f":material/{icon}: {label}"
        
        if st.button(btn_label, key=f"nav_{label}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = label
            st.rerun()

# ─── Page: Dashboard ──────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown('<div class="page-headline">Dashboard</div>', unsafe_allow_html=True)
    
    # ดึงข้อมูลที่จำเป็น
    stories = fetch_stories()
    episodes = fetch_episodes()
    incomes = fetch_incomes()

    # ─── Calculation Logic ───
    total_stories = len(stories) if not stories.empty else 0
    
    # คำนวณจำนวนคำทั้งหมดจาก episodes
    total_words = episodes["word_count"].sum() if not episodes.empty else 0
    
    # คำนวณรายได้รวม
    total_revenue = incomes["amount"].sum() if not incomes.empty else 0

    # ─── Metrics Row ───
    # ปรับเป็น 3 คอลัมน์: เรื่องทั้งหมด, จำนวนคำทั้งหมด, รายได้รวม
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Total Stories</div>
                <div class="metric-value">{total_stories:,}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with m2:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Total Word Count</div>
                <div class="metric-value">{total_words:,}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with m3:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">฿{total_revenue:,.2f}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Revenue over time chart
    col_chart, col_stories = st.columns([3, 2])

    with col_chart:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Revenue Over Time</div>', unsafe_allow_html=True)
        if not incomes.empty and "income_date" in incomes.columns:
            df_rev = incomes.copy()
            df_rev["income_date"] = pd.to_datetime(df_rev["income_date"])
            df_rev = df_rev.groupby(df_rev["income_date"].dt.to_period("M"))["amount"].sum().reset_index()
            df_rev["income_date"] = df_rev["income_date"].dt.to_timestamp()
            fig = go.Figure(go.Scatter(
                x=df_rev["income_date"], y=df_rev["amount"],
                fill="tozeroy", fillcolor="rgba(0,22,65,0.06)",
                line=dict(color="#001641", width=2),
                mode="lines+markers", marker=dict(size=5, color="#001641"),
            ))
            st.plotly_chart(styled_chart(fig), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<p style="color:var(--on-surface-variant);font-size:0.875rem">No income data yet.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_stories:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Stories by Status</div>', unsafe_allow_html=True)
        if not stories.empty and "status" in stories.columns:
            status_counts = stories["status"].value_counts()
            fig2 = go.Figure(go.Pie(
                labels=status_counts.index, values=status_counts.values,
                hole=0.55,
                marker=dict(colors=["#001641", "#545e7a", "#340a00", "#b1c5ff"]),
                textfont=dict(size=11, family="Inter"),
            ))
            fig2.update_traces(textposition="outside")
            st.plotly_chart(styled_chart(fig2), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<p style="color:var(--on-surface-variant);font-size:0.875rem">No stories yet.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Recent episodes table
    st.markdown('<div class="section-label" style="margin-top:0.5rem">Recent Episodes</div>', unsafe_allow_html=True)
    if not episodes.empty:
        df_ep = episodes[["episode_number", "title", "status", "word_count", "publish_date"]].head(10).copy()
        df_ep.columns = ["No.", "Title", "Status", "Words", "Published"]
        st.dataframe(df_ep, use_container_width=True, hide_index=True)
    else:
        st.info("No episodes found.")

# ─── Page: Analytics ──────────────────────────────────────────────────────────
def page_analytics():
    st.markdown('<div class="page-headline">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Deep dive into revenue performance and engagement correlations</div>', unsafe_allow_html=True)

    incomes = fetch_incomes()
    stats = fetch_statistics()

    if incomes.empty:
        st.info("No income data available for analysis.")
        return

    # ─── Data Preparation ───
    df_inc = incomes.copy()
    
    # Flatten ข้อมูลจาก Dictionary ให้เป็นคอลัมน์ปกติ
    df_inc['story_name'] = df_inc['stories'].apply(lambda x: x.get('title') if isinstance(x, dict) else "N/A")
    df_inc['platform_name'] = df_inc['platforms'].apply(lambda x: x.get('platform_name') if isinstance(x, dict) else "N/A")
    df_inc['income_type_name'] = df_inc['income_types'].apply(lambda x: x.get('income_type_name') if isinstance(x, dict) else "N/A")
    
    # แปลงวันที่ให้ชัวร์
    df_inc["income_date"] = pd.to_datetime(df_inc["income_date"])

    # ─── Filters ───
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        plat_list = ["All Platforms"] + sorted(df_inc["platform_name"].unique().tolist())
        sel_plat = st.selectbox("Filter by Platform", plat_list)
    with f2:
        type_list = ["All Types"] + sorted(df_inc["income_type_name"].unique().tolist())
        sel_type = st.selectbox("Filter by Income Type", type_list)
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply Filters
    if sel_plat != "All Platforms":
        df_inc = df_inc[df_inc["platform_name"] == sel_plat]
    if sel_type != "All Types":
        df_inc = df_inc[df_inc["income_type_name"] == sel_type]

    # ─── Top Metrics ───
    total_rev = df_inc["amount"].sum()
    count_rev = len(df_inc)
    avg_rev   = total_rev / count_rev if count_rev > 0 else 0

    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Revenue</div><div class="metric-value">฿{total_rev:,.2f}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">Transactions</div><div class="metric-value">{count_rev:,}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Average per Entry</div><div class="metric-value">฿{avg_rev:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Charts Row 1 ───
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Revenue by Platform</div>', unsafe_allow_html=True)
        # ตรวจสอบว่ามีข้อมูลก่อนวาด
        if not df_inc.empty:
            chart_data = df_inc.groupby("platform_name")["amount"].sum().reset_index()
            fig_plat = px.bar(chart_data, x="platform_name", y="amount", text_auto=".2s", color_discrete_sequence=["#001641"])
            st.plotly_chart(styled_chart(fig_plat), use_container_width=True)

    with c2:
        st.markdown('<div class="section-label">Top 5 Revenue-Generating Stories</div>', unsafe_allow_html=True)
        
        # 1. จัดกลุ่มและรวมยอดเงิน
        top_stories = df_inc.groupby("story_name")["amount"].sum().reset_index()
        
        # 2. จัดลำดับจากมากไปน้อย และเอาแค่ Top 5 (เพื่อไม่ให้มันเยอะจนซ้อนกัน)
        top_stories = top_stories.sort_values(ascending=False, by="amount").head(5)
        
        # 3. วาดกราฟ
        fig_story = px.bar(
            top_stories, 
            x="amount", 
            y="story_name", 
            orientation='h', 
            color_discrete_sequence=["#545e7a"],
            text_auto='.2s' # เพิ่มตัวเลขยอดเงินท้ายแท่งเพื่อให้ดูง่ายขึ้น
        )
        
        # 4. ปรับ Layout ให้แกน Y เรียงลำดับสวยงาม ไม่เบียด
        fig_story.update_layout(
            yaxis={'categoryorder':'total ascending'}, # เรียงแท่งที่ยาวที่สุดไว้ด้านบน
            margin=dict(l=20, r=20, t=20, b=20),     # เพิ่มพื้นที่ขอบ
            height=400                                # กำหนดความสูงให้คงที่
        )
        
        st.plotly_chart(styled_chart(fig_story), use_container_width=True)

    # ─── Revenue Trends ───
    st.markdown('<div class="section-label">Monthly Revenue Trend</div>', unsafe_allow_html=True)
    # ใช้ resample เพื่อให้เห็นแนวโน้มรายเดือนที่ถูกต้อง
    df_trend = df_inc.set_index("income_date").groupby("platform_name")["amount"].resample("MS").sum().reset_index()
    fig_trend = px.line(df_trend, x="income_date", y="amount", color="platform_name", markers=True)
    st.plotly_chart(styled_chart(fig_trend), use_container_width=True)

    # ─── Performance Correlation ───
    if not stats.empty:
        st.markdown('<div class="section-label">Engagement vs Revenue Analysis</div>', unsafe_allow_html=True)
        df_stats = stats.copy()
        df_stats['story_name'] = df_stats['stories'].apply(lambda x: x.get('title') if isinstance(x, dict) else "N/A")
        df_stats['platform_name'] = df_stats['platforms'].apply(lambda x: x.get('platform_name') if isinstance(x, dict) else "N/A")
        
        sum_inc = df_inc.groupby(["story_name", "platform_name"])["amount"].sum().reset_index()
        sum_stats = df_stats.groupby(["story_name", "platform_name"])[["view_count", "like_count", "comment_count"]].sum().reset_index()
        
        df_corr = pd.merge(sum_inc, sum_stats, on=["story_name", "platform_name"])
        
        if not df_corr.empty:
            metric_to_compare = st.radio("Select Metric:", ["view_count", "like_count", "comment_count"], horizontal=True)
            
            # 1. วาดกราฟโดย "ไม่ต้องใส่ title" ใน px.scatter
            fig_corr = px.scatter(
                df_corr, 
                x=metric_to_compare, 
                y="amount", 
                color="platform_name", 
                size="amount", 
                hover_name="story_name", 
                trendline="ols"
            )
            
            # 2. ตั้งค่า Margin เพื่อเพิ่มพื้นที่ด้านบนและด้านข้างให้หายใจออก
            fig_corr.update_layout(
                margin=dict(t=30, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # 3. แสดงชื่อกราฟด้วยสไตล์เดียวกับส่วนอื่นๆ ของแอป
            st.write(f"**Correlation Analysis: {metric_to_compare.replace('_', ' ').title()} vs Revenue**")
            
            st.plotly_chart(styled_chart(fig_corr), use_container_width=True)
            
# ─── Page: Stories ────────────────────────────────────────────────────────────
def page_stories():
    st.markdown('<div class="page-headline">Stories</div>', unsafe_allow_html=True)
    
    df_genres = fetch_genres()
    genre_options = df_genres['genre_name'].tolist() if not df_genres.empty else []

    tab_list, tab_add, tab_trash = st.tabs(["Catalogue", "Add Story", "Trash"])

    with tab_list:
        stories = fetch_stories()
        if not stories.empty:
            for _, row in stories.iterrows():
                current_genres = fetch_story_genres(row['story_id'])
                created_date = pd.to_datetime(row['created_at']).strftime('%d %b %Y') if pd.notnull(row['created_at']) else "N/A"
                
                # Header แบบทางการ
                header_text = f"{row['title']} — {', '.join(current_genres)} (Created: {created_date})"
                
                with st.expander(header_text):
                    with st.form(f"edit_story_{row['story_id']}"):
                        st.markdown('<div class="section-label">General Information</div>', unsafe_allow_html=True)
                        new_title = st.text_input("Title", value=row['title'])
                        new_desc = st.text_area("Description", value=row['description'])
                        
                        selected_genres = st.multiselect("Genres", options=genre_options, default=current_genres)
                        new_status = st.selectbox("Status", ["Published", "Hidden", "Archived"], 
                                                index=["Published", "Hidden", "Archived"].index(row['status']))
                        
                        st.divider()
                        # ปุ่มบันทึกและปุ่มลบ วางคู่กันชัดเจน
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button(":material/save: Save Changes", use_container_width=True):
                            supabase().table("stories").update({
                                "title": new_title, "description": new_desc, "status": new_status
                            }).eq("story_id", row['story_id']).execute()

                            supabase().table("story_genres").delete().eq("story_id", row['story_id']).execute()
                            if selected_genres:
                                new_genre_ids = df_genres[df_genres['genre_name'].isin(selected_genres)]['genre_id'].tolist()
                                insert_data = [{"story_id": int(row['story_id']), "genre_id": int(gid)} for gid in new_genre_ids]
                                supabase().table("story_genres").insert(insert_data).execute()
                            
                            clear_cache()
                            st.rerun()
                        
                        # ปุ่มลบแบบ Soft Delete
                        if c2.form_submit_button(":material/delete: Delete Story", use_container_width=True):
                            soft_delete("stories", "story_id", row['story_id'])
                            st.rerun()

    with tab_add:
        with st.form("add_story_new_form"):
            st.markdown('<div class="section-label">New Story Details</div>', unsafe_allow_html=True)
            add_title = st.text_input("Story Title")
            add_desc = st.text_area("Description")
            add_genres = st.multiselect("Select Genres", options=genre_options)
            add_status = st.selectbox("Status", ["Published", "Hidden", "Archived"])

            if st.form_submit_button(":material/add: Create Story", use_container_width=True):
                if add_title:
                    res = supabase().table("stories").insert({
                        "title": add_title, "description": add_desc, "status": add_status
                    }).execute()
                    new_id = res.data[0]['story_id']
                    if add_genres:
                        g_ids = df_genres[df_genres['genre_name'].isin(add_genres)]['genre_id'].tolist()
                        supabase().table("story_genres").insert([{"story_id": int(new_id), "genre_id": int(gid)} for gid in g_ids]).execute()
                    clear_cache()
                    st.rerun()

    with tab_trash:
        trash_stories = fetch_trash("stories")
        if not trash_stories.empty:
            for _, row in trash_stories.iterrows():
                c1, c2 = st.columns([4, 1])
                deleted_time = pd.to_datetime(row['deleted_at']).strftime('%d/%m/%Y %H:%M')
                c1.write(f"**{row['title']}** (Deleted at: {deleted_time})")
                if c2.button(":material/restore: Restore", key=f"res_story_{row['story_id']}", use_container_width=True):
                    restore_item("stories", "story_id", row['story_id'])
                    # กู้คืนลูกๆ ด้วย (Optional)
                    supabase().table("episodes").update({"deleted_at": None}).eq("story_id", row['story_id']).execute()
                    supabase().table("characters").update({"deleted_at": None}).eq("story_id", row['story_id']).execute()
                    st.rerun()
        else:
            st.info("Story trash is empty.")

# ─── Page: Episodes ───────────────────────────────────────────────────────────
def page_episodes():
    st.markdown('<div class="page-headline">Episodes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage chapters, word counts, and publication dates</div>', unsafe_allow_html=True)

    episodes = fetch_episodes()
    stories = fetch_stories()
    
    tab_list, tab_add, tab_trash = st.tabs(["Catalogue", "Add Episode", "Trash"])

    with tab_list:
        if not episodes.empty:
            story_titles = ["All Stories"] + list(stories['title'].unique())
            filter_story = st.selectbox("Filter by Story", story_titles)
            
            df_display = episodes.copy()
            if filter_story != "All Stories":
                df_display = df_display[df_display['stories'].apply(lambda x: x.get('title') == filter_story)]

            for _, row in df_display.iterrows():
                story_name = row['stories'].get('title', 'Unknown')
                created_date = pd.to_datetime(row['created_at']).strftime('%d %b %Y') if 'created_at' in row and pd.notnull(row['created_at']) else "N/A"
                
                # แสดงวันที่เผยแพร่ใน Header ถ้ามี
                pub_date_str = pd.to_datetime(row['publish_date']).strftime('%d/%m/%Y') if pd.notnull(row.get('publish_date')) else "Not set"
                header = f"Ep. {row['episode_number']}: {row['title']} ({story_name}) — {pub_date_str}"
                
                with st.expander(header):
                    with st.form(f"edit_ep_{row['episode_id']}"):
                        st.markdown('<div class="section-label">Episode Details</div>', unsafe_allow_html=True)
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            new_title = st.text_input("Episode Title", value=row['title'])
                            new_story = st.selectbox("Belongs to Story", stories['title'].tolist(), 
                                                   index=int(stories[stories['story_id'] == row['story_id']].index[0]) if not stories[stories['story_id'] == row['story_id']].empty else 0)
                            # เพิ่มช่อง Publish Date
                            current_pub_date = pd.to_datetime(row['publish_date']).date() if pd.notnull(row.get('publish_date')) else date.today()
                            new_pub_date = st.date_input("Publish Date", value=current_pub_date)

                        with e_col2:
                            new_num = st.number_input("Episode Number", value=int(row['episode_number']), step=1)
                            new_status = st.selectbox("Status", ["Draft", "Writing", "Published"], 
                                                    index=["Draft", "Writing", "Published"].index(row['status']) if row['status'] in ["Draft", "Writing", "Published"] else 0)
                            new_word_count = st.number_input("Word Count", value=int(row.get('word_count', 0)), min_value=0)

                        c1, c2 = st.columns(2)
                        if c1.form_submit_button(":material/save: Save Changes", use_container_width=True):
                            selected_story_id = int(stories[stories['title'] == new_story]['story_id'].values[0])
                            supabase().table("episodes").update({
                                "title": new_title,
                                "episode_number": int(new_num),
                                "status": new_status,
                                "story_id": selected_story_id,
                                "word_count": int(new_word_count),
                                "publish_date": new_pub_date.isoformat() # บันทึกวันที่
                            }).eq("episode_id", row['episode_id']).execute()
                            clear_cache()
                            st.success("Episode updated!")
                            st.rerun()
                        
                        if c2.form_submit_button(":material/delete: Delete", use_container_width=True):
                            soft_delete("episodes", "episode_id", row['episode_id'])
                            st.rerun()

    with tab_add:
        if stories.empty:
            st.warning("Please create a Story first.")
        else:
            with st.form("form_add_episode"):
                st.markdown('<div class="section-label">Create New Episode</div>', unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                with a1:
                    add_title = st.text_input("Episode Title")
                    add_story = st.selectbox("Select Story", stories['title'].tolist())
                    add_pub_date = st.date_input("Publish Date", value=date.today())
                with a2:
                    add_num = st.number_input("Episode Number", min_value=1, step=1)
                    add_word_count = st.number_input("Word Count", min_value=0)
                    add_status = st.selectbox("Status", ["Draft", "Writing", "Published"])
                
                if st.form_submit_button(":material/add: Create Episode"):
                    if add_title:
                        target_story_id = int(stories[stories['title'] == add_story]['story_id'].values[0])
                        supabase().table("episodes").insert({
                            "title": add_title,
                            "episode_number": int(add_num),
                            "story_id": target_story_id,
                            "status": add_status,
                            "word_count": int(add_word_count),
                            "publish_date": add_pub_date.isoformat()
                        }).execute()
                        clear_cache()
                        st.success("New episode added!")
                        st.rerun()

    with tab_trash:
        trash_eps = fetch_trash("episodes")
        if not trash_eps.empty:
            for _, row in trash_eps.iterrows():
                # เช็กชื่อเรื่องจากข้อมูลที่ดึงมา
                story_name = row['stories'].get('title', 'Unknown Story') if isinstance(row.get('stories'), dict) else "Unknown"
                c1, c2 = st.columns([4, 1])
                c1.write(f"**Ep. {row['episode_number']}: {row['title']}** (Story: {story_name})")
                if c2.button(":material/restore: Restore", key=f"res_ep_{row['episode_id']}", use_container_width=True):
                    restore_item("episodes", "episode_id", row['episode_id'])
                    st.rerun()
        else:
            st.info("Episode trash is empty.")


# ─── Page: Characters ─────────────────────────────────────────────────────────
def page_characters():
    st.markdown('<div class="page-headline">Characters</div>', unsafe_allow_html=True)
    
    # ดึงข้อมูล (มั่นใจว่า fetch_stories และ fetch_characters กรอง deleted_at is null แล้ว)
    chars = fetch_characters()
    stories = fetch_stories()
    
    tab_list, tab_add, tab_trash = st.tabs(["Registry", "Add Character", "Trash"])

    with tab_list:
        if not chars.empty:
            # ─── ส่วนของ FILTER BY STORY ───
            story_names = ["All Stories"] + sorted(stories['title'].unique().tolist()) if not stories.empty else ["All Stories"]
            selected_story = st.selectbox("Filter by Story", story_names)
            
            df_display = chars.copy()
            if selected_story != "All Stories":
                # กรองโดยเช็กจาก nested object 'stories' -> 'title'
                df_display = df_display[df_display['stories'].apply(lambda x: x.get('title') == selected_story)]

            if df_display.empty:
                st.info(f"No characters found for '{selected_story}'")
            else:
                for _, row in df_display.iterrows():
                    story_name = row['stories'].get('title', 'Unknown')
                    header = f"{row['name']} — {row['role']} ({story_name})"
                    
                    with st.expander(header):
                        with st.form(f"edit_char_{row['character_id']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                new_name = st.text_input("Name", value=row['name'])
                                story_list = stories['title'].tolist() if not stories.empty else [story_name]
                                current_story_idx = story_list.index(story_name) if story_name in story_list else 0
                                new_story = st.selectbox("Story", story_list, index=current_story_idx)
                                new_role = st.selectbox("Role", ["Main", "Support"], index=["Main", "Support"].index(row['role']))
                            with c2:
                                new_age = st.number_input("Age", value=int(row['age']) if row['age'] else 0)
                                new_occ = st.text_input("Occupation", value=row['occupation'] if row['occupation'] else "")

                            st.divider()
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button(":material/save: Save Changes", use_container_width=True):
                                sid = int(stories[stories['title'] == new_story]['story_id'].values[0])
                                supabase().table("characters").update({
                                    "name": new_name, "story_id": sid, "role": new_role,
                                    "age": int(new_age), "occupation": new_occ
                                }).eq("character_id", row['character_id']).execute()
                                clear_cache(); st.rerun()
                            
                            if b2.form_submit_button(":material/delete: Delete", use_container_width=True):
                                soft_delete("characters", "character_id", row['character_id'])
                                st.rerun()
        else:
            st.info("No active characters found.")

    with tab_add:
        with st.form("add_char_form"):
            st.markdown('<div class="section-label">New Character</div>', unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            story_options = stories['title'].tolist() if not stories.empty else []
            
            with a1:
                add_name = st.text_input("Name")
                add_story = st.selectbox("Select Story", story_options if story_options else ["No stories available"])
            with a2:
                add_role = st.selectbox("Role", ["Main", "Support"])
                add_age = st.number_input("Age", min_value=0)
            
            add_occ = st.text_input("Occupation")
            if st.form_submit_button(":material/add: Create"):
                if add_name and not stories.empty and add_story != "No stories available":
                    sid = int(stories[stories['title'] == add_story]['story_id'].values[0])
                    supabase().table("characters").insert({
                        "name": add_name, "story_id": sid, "role": add_role, "age": int(add_age), "occupation": add_occ
                    }).execute()
                    clear_cache(); st.rerun()

    with tab_trash:
        trash_chars = fetch_trash("characters")
        if not trash_chars.empty:
            for _, row in trash_chars.iterrows():
                story_name = row['stories'].get('title', 'Unknown') if isinstance(row.get('stories'), dict) else "N/A"
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['name']}** ({row['role']}) - Story: {story_name}\n\n*Deleted: {row['deleted_at']}*")
                if c2.button(":material/restore: Restore", key=f"res_char_{row['character_id']}", use_container_width=True):
                    restore_item("characters", "character_id", row['character_id'])
                    st.rerun()
        else:
            st.info("Character trash is empty.")

# ─── Page: revenue ─────────────────────────────────────────────────────────
def page_revenue():
    st.markdown('<div class="page-headline">Revenue</div>', unsafe_allow_html=True)
    
    incomes = fetch_incomes()
    stories = fetch_stories()
    platforms = fetch_platforms()
    types = fetch_income_types()
    all_episodes = fetch_episodes()

    tab_list, tab_add, tab_trash = st.tabs(["Transactions", "Add Record", "Trash"])

    with tab_list:
        if not incomes.empty:
            story_names = ["All Stories"] + sorted(stories['title'].unique().tolist()) if not stories.empty else ["All Stories"]
            selected_story_filter = st.selectbox("Filter by Story", story_names, key="rev_filter_story")
            
            df_display = incomes.copy()
            if selected_story_filter != "All Stories":
                df_display = df_display[df_display['stories'].apply(lambda x: x.get('title') == selected_story_filter)]

            if df_display.empty:
                st.info(f"No transactions found for '{selected_story_filter}'")
            else:
                for _, row in df_display.iterrows():
                    # 1. เตรียมข้อมูลแสดงผล
                    story_name = row['stories'].get('title', 'Unknown Story') if isinstance(row['stories'], dict) else "N/A"
                    plat_name = row['platforms'].get('platform_name', 'N/A') if isinstance(row['platforms'], dict) else "N/A"
                    
                    type_data = row.get('income_types')
                    type_name = type_data.get('income_type_name', 'N/A') if isinstance(type_data, dict) else "N/A"
                    
                    ep_data = row.get('episodes')
                    ep_info = f" (Ep. {ep_data.get('episode_number')})" if isinstance(ep_data, dict) and ep_data.get('episode_number') else ""
                    
                    # Header ที่รวมประเภทรายได้ตามที่คุณต้องการ
                    header = f"฿{row['amount']:,.2f} | {story_name}{ep_info} | {type_name} | {plat_name} | {row['income_date']}"
                    
                    with st.expander(header):
                        # ─── FORM สำหรับ EDIT ───
                        with st.form(f"edit_rev_{row['income_id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_amt = st.number_input("Amount (฿)", value=float(row['amount']))
                                
                                s_list = stories['title'].tolist()
                                s_idx = s_list.index(story_name) if story_name in s_list else 0
                                edit_story = st.selectbox("Story", s_list, index=s_idx)
                                
                                # ดึงตอนตามเรื่องที่เลือก
                                curr_sid = stories[stories['title'] == edit_story]['story_id'].values[0]
                                rel_eps = all_episodes[all_episodes['story_id'] == curr_sid]
                                ep_opts = ["None"] + [f"Ep. {int(n)}: {t}" for n, t in zip(rel_eps['episode_number'], rel_eps['title'])]
                                
                                # หาค่า Default ของ Episode
                                curr_ep_val = "None"
                                if isinstance(ep_data, dict) and 'episode_number' in ep_data:
                                    curr_ep_val = f"Ep. {int(ep_data['episode_number'])}: {ep_data['title']}"
                                
                                ep_idx = ep_opts.index(curr_ep_val) if curr_ep_val in ep_opts else 0
                                edit_ep = st.selectbox("Episode", ep_opts, index=ep_idx)

                            with col2:
                                p_list = platforms['platform_name'].tolist()
                                p_idx = p_list.index(plat_name) if plat_name in p_list else 0
                                edit_plat = st.selectbox("Platform", p_list, index=p_idx)
                                
                                t_list = types['income_type_name'].tolist()
                                t_idx = t_list.index(type_name) if type_name in t_list else 0
                                edit_type = st.selectbox("Income Type", t_list, index=t_idx)
                                
                                edit_date = st.date_input("Date", value=pd.to_datetime(row['income_date']).date())

                            st.divider()
                            c_save, c_del = st.columns(2)
                            
                            if c_save.form_submit_button(":material/save: Save Changes", use_container_width=True):
                                # Logic การ Update
                                new_sid = int(stories[stories['title'] == edit_story]['story_id'].values[0])
                                new_pid = int(platforms[platforms['platform_name'] == edit_plat]['platform_id'].values[0])
                                new_tid = int(types[types['income_type_name'] == edit_type]['income_type_id'].values[0])
                                
                                new_eid = None
                                if edit_ep != "None":
                                    target_num = int(edit_ep.split(":")[0].replace("Ep. ", ""))
                                    eid_row = rel_eps[rel_eps['episode_number'] == target_num]
                                    if not eid_row.empty:
                                        new_eid = int(eid_row['episode_id'].values[0])

                                supabase().table("incomes").update({
                                    "amount": edit_amt,
                                    "story_id": new_sid,
                                    "platform_id": new_pid,
                                    "income_type_id": new_tid,
                                    "episode_id": new_eid,
                                    "income_date": edit_date.isoformat()
                                }).eq("income_id", row['income_id']).execute()
                                
                                clear_cache(); st.rerun()

                            if c_del.form_submit_button(":material/delete: Delete", use_container_width=True):
                                soft_delete("incomes", "income_id", row['income_id'])
                                st.rerun()
        else:
            st.info("No revenue records found.")

    with tab_add:
        if stories.empty or platforms.empty or types.empty:
            st.warning("Please ensure you have Stories, Platforms, and Income Types set up in Settings.")
        else:
            with st.form("add_revenue_form"):
                st.markdown('<div class="section-label">Add New Transaction</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    add_amt = st.number_input("Amount (฿)", min_value=0.0, step=100.0)
                    add_story = st.selectbox("Related Story", stories['title'].tolist())
                    
                    # Logic เลือก Episode: กรองเฉพาะของ Story ที่เลือก
                    current_sid = stories[stories['title'] == add_story]['story_id'].values[0]
                    relevant_eps = all_episodes[all_episodes['story_id'] == current_sid]
                    ep_options = ["None"] + [f"Ep. {int(n)}: {t}" for n, t in zip(relevant_eps['episode_number'], relevant_eps['title'])]
                    add_ep = st.selectbox("Related Episode (Optional)", ep_options)

                with col2:
                    add_plat = st.selectbox("Platform", platforms['platform_name'].tolist())
                    add_type = st.selectbox("Income Type", types['income_type_name'].tolist())
                    add_date = st.date_input("Transaction Date", value=date.today())
                
                if st.form_submit_button(":material/add: Save Transaction", use_container_width=True):
                    # เตรียมข้อมูล ID
                    sid = int(current_sid)
                    pid = int(platforms[platforms['platform_name'] == add_plat]['platform_id'].values[0])
                    tid = int(types[types['income_type_name'] == add_type]['income_type_id'].values[0])
                    
                    # ดึง Episode ID (ถ้าเลือก)
                    eid = None
                    if add_ep != "None":
                        # แยกเอาเฉพาะเลขตอนออกมาเพื่อไปหา ID
                        target_ep_num = int(add_ep.split(":")[0].replace("Ep. ", ""))
                        eid_row = relevant_eps[relevant_eps['episode_number'] == target_ep_num]
                        if not eid_row.empty:
                            eid = int(eid_row['episode_id'].values[0])
                    
                    supabase().table("incomes").insert({
                        "amount": add_amt,
                        "story_id": sid,
                        "platform_id": pid,
                        "income_type_id": tid,
                        "episode_id": eid,
                        "income_date": add_date.isoformat()
                    }).execute()
                    clear_cache()
                    st.success("Revenue added successfully!")
                    st.rerun()

    with tab_trash:
        # ใช้ fetch_trash ที่เราแก้ให้ดึง stories(title) มาแล้ว
        trash = fetch_trash("incomes")
        if not trash.empty:
            for _, row in trash.iterrows():
                amt = row.get('amount', 0)
                # ดึงชื่อเรื่องมาโชว์ในถังขยะด้วย
                s_name = row['stories'].get('title', 'N/A') if isinstance(row.get('stories'), dict) else "N/A"
                del_date = pd.to_datetime(row['deleted_at']).strftime('%d/%m/%Y %H:%M')
                
                c1, c2 = st.columns([4, 1])
                c1.write(f"**฿{amt:,.2f}** ({s_name}) | Deleted: {del_date}")
                if c2.button(":material/restore: Restore", key=f"res_rev_{row['income_id']}", use_container_width=True):
                    restore_item("incomes", "income_id", row['income_id'])
                    st.rerun()
        else:
            st.info("Trash is empty.")


# ─── Page: Statistics ─────────────────────────────────────────────────────────
def page_statistics():
    st.markdown('<div class="page-headline">Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Engagement data across platforms</div>', unsafe_allow_html=True)

    tab_view, tab_add, tab_trash = st.tabs(["Performance Data", "Add Record", "Trash"])
    stats     = fetch_statistics()
    stories   = fetch_stories()
    platforms = fetch_platforms()

    with tab_view:
        if not stats.empty:
            # กรองเฉพาะรายการที่ยังไม่ได้ลบ (deleted_at is null)
            # หมายเหตุ: fetch_statistics เดิมอาจจะดึงมาทั้งหมด ควรตรวจสอบ query ใน fetch_statistics ด้วย
            df_active = stats[stats['deleted_at'].isna()] if 'deleted_at' in stats.columns else stats
            
            if df_active.empty:
                st.info("No active statistics recorded yet.")
            else:
                # ─── Metrics Summary ───
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Views</div><div class="metric-value">{int(df_active["view_count"].sum()):,}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Likes</div><div class="metric-value">{int(df_active["like_count"].sum()):,}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Comments</div><div class="metric-value">{int(df_active["comment_count"].sum()):,}</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ─── List & Edit Form ───
                for _, row in df_active.iterrows():
                    s_name = row['stories'].get('title', 'Unknown') if isinstance(row['stories'], dict) else "N/A"
                    p_name = row['platforms'].get('platform_name', 'N/A') if isinstance(row['platforms'], dict) else "N/A"
                    header = f"{row['recorded_at']} | {s_name} | {p_name} (Views: {int(row['view_count']):,})"
                    
                    with st.expander(header):
                        with st.form(f"edit_stat_{row['stat_id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                # ค้นหา story_id และ platform_id จากชื่อเดิม
                                s_list = stories['title'].tolist() if not stories.empty else []
                                s_idx = s_list.index(s_name) if s_name in s_list else 0
                                edit_story = st.selectbox("Story", s_list, index=s_idx)
                                
                                edit_views = st.number_input("Views", value=int(row['view_count']), min_value=0)
                                edit_likes = st.number_input("Likes", value=int(row['like_count']), min_value=0)
                            
                            with col2:
                                p_list = platforms['platform_name'].tolist() if not platforms.empty else []
                                p_idx = p_list.index(p_name) if p_name in p_list else 0
                                edit_plat = st.selectbox("Platform", p_list, index=p_idx)
                                
                                edit_comments = st.number_input("Comments", value=int(row['comment_count']), min_value=0)
                                edit_date = st.date_input("Recorded Date", value=pd.to_datetime(row['recorded_at']).date())

                            st.divider()
                            btn_save, btn_del = st.columns(2)
                            
                            if btn_save.form_submit_button(":material/save: Save Changes", use_container_width=True):
                                sid = int(stories[stories['title'] == edit_story]['story_id'].values[0])
                                pid = int(platforms[platforms['platform_name'] == edit_plat]['platform_id'].values[0])
                                
                                supabase().table("statistics").update({
                                    "story_id": sid,
                                    "platform_id": pid,
                                    "view_count": int(edit_views),
                                    "like_count": int(edit_likes),
                                    "comment_count": int(edit_comments),
                                    "recorded_at": edit_date.isoformat()
                                }).eq("stat_id", row['stat_id']).execute()
                                
                                clear_cache(); st.rerun()

                            if btn_del.form_submit_button(":material/delete: Delete", use_container_width=True):
                                soft_delete("statistics", "stat_id", row['stat_id'])
                                st.rerun()
        else:
            st.info("No statistics recorded yet.")

    with tab_add:
        with st.form("form_add_stat"):
            st.markdown('<div class="section-label">Add Statistics Record</div>', unsafe_allow_html=True)
            story_opts = stories['title'].tolist() if not stories.empty else []
            plat_opts = platforms['platform_name'].tolist() if not platforms.empty else []

            col1, col2 = st.columns(2)
            with col1:
                add_story = st.selectbox("Story", story_opts if story_opts else ["—"])
                add_views = st.number_input("Views", min_value=0, step=1)
                add_likes = st.number_input("Likes", min_value=0, step=1)
            with col2:
                add_plat = st.selectbox("Platform", plat_opts if plat_opts else ["—"])
                add_comments = st.number_input("Comments", min_value=0, step=1)
                add_date = st.date_input("Recorded Date", value=date.today())

            if st.form_submit_button(":material/add: Save Record", use_container_width=True):
                if not stories.empty and not platforms.empty:
                    sid = int(stories[stories['title'] == add_story]['story_id'].values[0])
                    pid = int(platforms[platforms['platform_name'] == add_plat]['platform_id'].values[0])
                    
                    supabase().table("statistics").insert({
                        "story_id": sid,
                        "platform_id": pid,
                        "view_count": int(add_views),
                        "like_count": int(add_likes),
                        "comment_count": int(add_comments),
                        "recorded_at": add_date.isoformat(),
                    }).execute()
                    clear_cache(); st.success("Statistics saved."); st.rerun()
                else:
                    st.error("Please ensure stories and platforms exist.")

    with tab_trash:
        trash_stats = fetch_trash("statistics")
        if not trash_stats.empty:
            for _, row in trash_stats.iterrows():
                s_name = row['stories'].get('title', 'Unknown') if isinstance(row['stories'], dict) else "N/A"
                del_time = pd.to_datetime(row['deleted_at']).strftime('%d/%m/%Y %H:%M')
                
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{s_name}** ({row['recorded_at']}) | Views: {int(row['view_count']):,} | Deleted: {del_time}")
                if c2.button(":material/restore: Restore", key=f"res_stat_{row['stat_id']}", use_container_width=True):
                    restore_item("statistics", "stat_id", row['stat_id'])
                    st.rerun()
        else:
            st.info("Statistics trash is empty.")


# ─── Page: Settings ───────────────────────────────────────────────────────────
def page_settings():
    st.markdown('<div class="page-headline">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Manage reference data — platforms, genres, income types</div>', unsafe_allow_html=True)

    tab_plat, tab_genre, tab_itype = st.tabs(["Platforms", "Genres", "Income Types"])

    with tab_plat:
        platforms = fetch_platforms()
        if not platforms.empty:
            st.dataframe(platforms[["platform_id", "platform_name"]].rename(columns={"platform_id": "ID", "platform_name": "Platform"}), use_container_width=True, hide_index=True)
        with st.form("form_add_platform"):
            name = st.text_input("New Platform Name")
            if st.form_submit_button("Add Platform"):
                if name:
                    supabase().table("platforms").insert({"platform_name": name}).execute()
                    clear_cache(); st.success("Platform added."); st.rerun()

    with tab_genre:
        genres = fetch_genres()
        if not genres.empty:
            st.dataframe(genres[["genre_id", "genre_name"]].rename(columns={"genre_id": "ID", "genre_name": "Genre"}), use_container_width=True, hide_index=True)
        with st.form("form_add_genre"):
            name = st.text_input("New Genre Name")
            if st.form_submit_button("Add Genre"):
                if name:
                    supabase().table("genres").insert({"genre_name": name}).execute()
                    clear_cache(); st.success("Genre added."); st.rerun()

    with tab_itype:
        itypes = fetch_income_types()
        if not itypes.empty:
            st.dataframe(itypes[["income_type_id", "income_type_name"]].rename(columns={"income_type_id": "ID", "income_type_name": "Income Type"}), use_container_width=True, hide_index=True)
        with st.form("form_add_itype"):
            name = st.text_input("New Income Type Name")
            if st.form_submit_button("Add Income Type"):
                if name:
                    supabase().table("income_types").insert({"income_type_name": name}).execute()
                    clear_cache(); st.success("Income type added."); st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "Dashboard")

if page == "Dashboard":  page_dashboard()
elif page == "Analytics": page_analytics()
elif page == "Stories":  page_stories()
elif page == "Episodes": page_episodes()
elif page == "Characters": page_characters()
elif page == "Revenue":  page_revenue()
elif page == "Statistics": page_statistics()
elif page == "Settings": page_settings()
