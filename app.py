"""
==============================================================================
MODULE: app.py  —  VENDI TERA Premium
PROJECT: Movie Recommendation System
==============================================================================
"""

import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="VENDI TERA — Premium Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# API KEY — set TMDB_API_KEY as an environment variable in Render dashboard
# ═══════════════════════════════════════════════════════════════════════════════
import os
# Support both Streamlit Cloud secrets and environment variables
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "") if hasattr(st, "secrets") else ""
if not TMDB_API_KEY:
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
if not TMDB_API_KEY:
    st.error("⚠️ TMDB_API_KEY is not set. Add it in Streamlit Cloud → App Settings → Secrets.")
    st.stop()
TMDB_IMG     = "https://image.tmdb.org/t/p/w342"
TMDB_IMG_LG  = "https://image.tmdb.org/t/p/w500"

# ═══════════════════════════════════════════════════════════════════════════════
# LUXURY VENDIMA CSS
# Color proportions:
#   70%  →  Obsidian base  (#07070b, #0d0d14, #111119)
#   20%  →  Warm charcoal surface  (#1c1c27, #23232f, #2a2a38)
#   10%  →  Amber-gold accent  (#c9a84c, #e2c272, #f0d080)
#   <1%  →  Crimson highlight  (#9b1d20)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=Outfit:wght@200;300;400;500;600&display=swap');

/* ─── RESET & ROOT ──────────────────────────────────────────────────────── */
:root {
  --ob1:   #07070b;
  --ob2:   #0d0d14;
  --ob3:   #111119;
  --s1:    #1c1c27;
  --s2:    #23232f;
  --s3:    #2a2a38;
  --b1:    #35354a;
  --b2:    #42425a;
  --gold1: #c9a84c;
  --gold2: #e2c272;
  --gold3: #f0d080;
  --crim:  #9b1d20;
  --tx1:   #f0ece4;
  --tx2:   #b8b4aa;
  --tx3:   #7a7870;
  --rad:   radial-gradient(ellipse at 20% 0%, rgba(201,168,76,0.07) 0%, transparent 60%),
           radial-gradient(ellipse at 80% 100%, rgba(155,29,32,0.06) 0%, transparent 60%);
}

/* ─── BASE ──────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  background: var(--ob1);
  color: var(--tx1);
}
.stApp {
  background: var(--ob1);
  background-image: var(--rad);
  background-attachment: fixed;
}
.block-container {
  padding: 0 2.5rem 4rem !important;
  max-width: 1380px !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
.stDeployButton, [data-testid="stToolbar"] { visibility: hidden; height: 0; }
section[data-testid="stSidebar"] { display: none; }

/* ─── SCROLLBAR ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--ob2); }
::-webkit-scrollbar-thumb { background: var(--gold1); border-radius: 2px; }

/* ─── TOPBAR ────────────────────────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.6rem 0 1.2rem;
  border-bottom: 1px solid var(--b1);
  margin-bottom: 0;
}
.logo {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--tx1);
}
.logo em { color: var(--gold1); font-style: normal; }
.logo-dot {
  display: inline-block;
  width: 6px; height: 6px;
  background: var(--gold1);
  border-radius: 50%;
  margin: 0 4px 2px;
  vertical-align: middle;
}
.topbar-tag {
  font-family: 'Outfit', sans-serif;
  font-size: 0.7rem;
  font-weight: 300;
  letter-spacing: 0.25em;
  color: var(--tx3);
  text-transform: uppercase;
}

/* ─── HERO ──────────────────────────────────────────────────────────────── */
.hero-wrap {
  position: relative;
  padding: 5rem 0 4rem;
  text-align: center;
  overflow: hidden;
}
.hero-wrap::before {
  content: '';
  position: absolute;
  top: -60px; left: 50%;
  transform: translateX(-50%);
  width: 600px; height: 300px;
  background: radial-gradient(ellipse, rgba(201,168,76,0.13) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'Outfit', sans-serif;
  font-size: 0.68rem;
  font-weight: 400;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: var(--gold1);
  margin-bottom: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.hero-eyebrow::before,
.hero-eyebrow::after {
  content: '';
  display: inline-block;
  width: 40px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold1));
}
.hero-eyebrow::after { background: linear-gradient(90deg, var(--gold1), transparent); }
.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(3.5rem, 8vw, 6.5rem);
  font-weight: 300;
  line-height: 1.0;
  color: var(--tx1);
  letter-spacing: -0.01em;
  margin-bottom: 1.4rem;
}
.hero-title strong {
  font-weight: 700;
  color: var(--gold2);
  display: block;
}
.hero-sub {
  font-family: 'Outfit', sans-serif;
  font-size: 0.95rem;
  font-weight: 300;
  color: var(--tx3);
  letter-spacing: 0.04em;
  max-width: 480px;
  margin: 0 auto;
}

/* ─── SEARCH SECTION ────────────────────────────────────────────────────── */
.search-wrap {
  max-width: 760px;
  margin: 0 auto 3rem;
  padding: 2.2rem 2.5rem;
  background: var(--s1);
  border: 1px solid var(--b1);
  border-radius: 4px;
  position: relative;
}
.search-wrap::before {
  content: '';
  position: absolute;
  top: 0; left: 2.5rem; right: 2.5rem;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold1), transparent);
}
.search-label {
  font-family: 'Outfit', sans-serif;
  font-size: 0.68rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--gold1);
  margin-bottom: 0.8rem;
  display: block;
}

/* Streamlit selectbox */
.stSelectbox > div > div {
  background: var(--ob2) !important;
  border: 1px solid var(--b2) !important;
  border-radius: 3px !important;
  color: var(--tx1) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1rem !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--gold1) !important;
  box-shadow: 0 0 0 1px var(--gold1) !important;
}
[data-baseweb="select"] { background: var(--ob2) !important; }
[data-baseweb="popover"] { background: var(--s1) !important; border: 1px solid var(--b2) !important; }
[role="option"]:hover { background: var(--s2) !important; }
[role="option"][aria-selected="true"] { background: var(--s3) !important; }

/* ─── BUTTON ────────────────────────────────────────────────────────────── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--gold1) !important;
  color: var(--gold1) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.25em !important;
  text-transform: uppercase !important;
  padding: 0.75rem 2rem !important;
  width: 100% !important;
  border-radius: 2px !important;
  transition: all 0.25s ease !important;
  margin-top: 0.8rem !important;
}
.stButton > button:hover {
  background: var(--gold1) !important;
  color: var(--ob1) !important;
  box-shadow: 0 0 24px rgba(201,168,76,0.25) !important;
}

/* ─── STATS BAR ─────────────────────────────────────────────────────────── */
.stats-bar {
  display: flex;
  border-top: 1px solid var(--b1);
  border-bottom: 1px solid var(--b1);
  margin-bottom: 3.5rem;
}
.stat-item {
  flex: 1;
  padding: 1.4rem 0;
  text-align: center;
  border-right: 1px solid var(--b1);
  position: relative;
}
.stat-item:last-child { border-right: none; }
.stat-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.2rem;
  font-weight: 600;
  color: var(--gold2);
  line-height: 1;
  display: block;
}
.stat-lbl {
  font-family: 'Outfit', sans-serif;
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--tx3);
  margin-top: 0.3rem;
  display: block;
}

/* ─── SECTION HEADER ────────────────────────────────────────────────────── */
.sec-header {
  display: flex;
  align-items: baseline;
  gap: 1.2rem;
  margin-bottom: 2rem;
  padding-bottom: 0.9rem;
  border-bottom: 1px solid var(--b1);
}
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.6rem;
  font-weight: 400;
  color: var(--tx1);
  font-style: italic;
}
.sec-query {
  font-style: normal;
  font-weight: 700;
  color: var(--gold2);
}
.sec-count {
  font-family: 'Outfit', sans-serif;
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--tx3);
  margin-left: auto;
}

/* ─── MOVIE CARD ─────────────────────────────────────────────────────────── */
.card {
  background: var(--s1);
  border: 1px solid var(--b1);
  border-radius: 4px;
  display: flex;
  gap: 0;
  margin-bottom: 1.2rem;
  overflow: hidden;
  transition: border-color 0.3s, box-shadow 0.3s;
  position: relative;
}
.card:hover {
  border-color: var(--gold1);
  box-shadow: 0 8px 40px rgba(201,168,76,0.08), 0 2px 8px rgba(0,0,0,0.4);
}
.card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.card:hover::after { opacity: 1; }

.card-poster {
  width: 100px;
  min-width: 100px;
  background: var(--ob2);
  overflow: hidden;
  position: relative;
}
.card-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: brightness(0.92);
  transition: filter 0.3s;
}
.card:hover .card-poster img { filter: brightness(1.05); }
.card-poster-placeholder {
  width: 100%;
  height: 100%;
  min-height: 148px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  background: linear-gradient(160deg, var(--s2), var(--ob2));
}

.card-body {
  flex: 1;
  padding: 1.1rem 1.4rem 1.1rem 1.3rem;
  min-width: 0;
}
.card-rank {
  position: absolute;
  top: 0.7rem; right: 1rem;
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--b1);
  line-height: 1;
  user-select: none;
}
.card-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.18rem;
  font-weight: 600;
  color: var(--tx1);
  margin-bottom: 0.25rem;
  line-height: 1.25;
  padding-right: 2.5rem;
}
.card-meta {
  font-family: 'Outfit', sans-serif;
  font-size: 0.75rem;
  color: var(--tx3);
  margin-bottom: 0.6rem;
  letter-spacing: 0.02em;
}
.card-meta b { color: var(--tx2); font-weight: 500; }
.card-overview {
  font-family: 'Outfit', sans-serif;
  font-size: 0.82rem;
  font-weight: 300;
  color: var(--tx2);
  line-height: 1.6;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 0.7rem;
}
.tag {
  font-family: 'Outfit', sans-serif;
  font-size: 0.65rem;
  font-weight: 400;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold1);
  border: 1px solid rgba(201,168,76,0.3);
  padding: 2px 9px;
  border-radius: 1px;
  background: rgba(201,168,76,0.05);
}
.card-score-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.score-track {
  flex: 1;
  height: 2px;
  background: var(--b1);
  border-radius: 1px;
  overflow: hidden;
}
.score-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--crim), var(--gold1), var(--gold3));
  border-radius: 1px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.score-pct {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--gold2);
  min-width: 42px;
  text-align: right;
}
.score-stars {
  font-size: 0.65rem;
  color: var(--gold1);
  letter-spacing: 1px;
}

/* ─── RATING BADGE ──────────────────────────────────────────────────────── */
.rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(201,168,76,0.1);
  border: 1px solid rgba(201,168,76,0.25);
  border-radius: 2px;
  padding: 1px 7px;
  font-family: 'Outfit', sans-serif;
  font-size: 0.72rem;
  color: var(--gold2);
  font-weight: 500;
}

/* ─── DIVIDER ────────────────────────────────────────────────────────────── */
.ornament-divider {
  text-align: center;
  margin: 3rem 0;
  color: var(--b2);
  font-size: 1.1rem;
  letter-spacing: 0.5em;
  user-select: none;
}
.ornament-divider::before,
.ornament-divider::after {
  content: '';
  display: inline-block;
  width: 80px; height: 1px;
  background: var(--b1);
  vertical-align: middle;
  margin: 0 16px;
}

/* ─── EMPTY STATE ────────────────────────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  color: var(--tx3);
}
.empty-state .es-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.4;
}
.empty-state p {
  font-family: 'Outfit', sans-serif;
  font-size: 0.9rem;
  font-weight: 300;
  letter-spacing: 0.08em;
}

/* ─── SLIDER ────────────────────────────────────────────────────────────── */
.stSlider > div { color: var(--tx2) !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
  background: var(--gold1) !important;
}

/* ─── FOOTER ─────────────────────────────────────────────────────────────── */
.footer {
  text-align: center;
  padding: 2.5rem 0 1rem;
  border-top: 1px solid var(--b1);
  margin-top: 4rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--tx3);
}
.footer em { color: var(--gold1); font-style: normal; }

/* ─── DOWNLOAD BTN ───────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
  background: transparent !important;
  border: 1px solid var(--b2) !important;
  color: var(--tx3) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  border-radius: 2px !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--gold1) !important;
  color: var(--gold1) !important;
}

/* ─── EXPANDER ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--s1) !important;
  border: 1px solid var(--b1) !important;
  border-radius: 3px !important;
}

/* ─── SPINNER ────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--gold1) !important; }

/* ─── SLIDER CONTROLS ────────────────────────────────────────────────────── */
.controls-strip {
  display: flex;
  gap: 2rem;
  align-items: flex-end;
  max-width: 760px;
  margin: 0 auto 0.5rem;
  padding: 0 0.2rem;
}
.ctrl-label {
  font-family: 'Outfit', sans-serif;
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--tx3);
  margin-bottom: 0.4rem;
  display: block;
}
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from api_client import build_movie_dataset, clear_cache
from preprocessor import build_dataframe
from recommender import MovieRecommender

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("recs", None), ("query", ""), ("elapsed", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <div class="logo">VENDI<span class="logo-dot"></span><em> TERA</em></div>
  <div class="topbar-tag">Intelligent Film Discovery</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">AI-Powered Recommendation Engine</div>
  <h1 class="hero-title">
    Discover Films
    <strong>Made for You</strong>
  </h1>
  <p class="hero-sub">Enter any movie and our algorithm surfaces the most relevant titles across genre, theme, cast, and narrative</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD ENGINE (background, no spinner visible)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_engine(pages: int = 25):
    movies = build_movie_dataset(TMDB_API_KEY, pages=pages)
    df     = build_dataframe(movies)
    engine = MovieRecommender().fit(df)
    return engine, df

# Controls strip (above search box)
st.markdown('<div class="controls-strip">', unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
with c1:
    pages = st.slider("🎞️ Movie Library Size (pages × 20 = total movies)", 5, 80, 25, 5,
                      help="Pages × 20 = movies fetched from TMDB. More pages = richer recommendations but slower first load.")
with c2:
    top_n = st.slider("🎯 No. of Recommendations", 3, 16, 8,
                      help="How many similar movies to show in results.")
st.markdown('</div>', unsafe_allow_html=True)

with st.spinner(""):
    try:
        engine, df = load_engine(pages)
    except Exception as e:
        st.error(f"Failed to connect to TMDB: {e}")
        st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH BOX
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="search-wrap">
  <span class="search-label">Select or search a film title</span>
""", unsafe_allow_html=True)

scol1, scol2 = st.columns([5, 1])
with scol1:
    selected = st.selectbox(
        "film", [""] + sorted(engine.all_titles),
        label_visibility="collapsed",
        placeholder="e.g. Inception, The Dark Knight, Parasite …"
    )
with scol2:
    go = st.button("Discover", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STATS BAR
# ═══════════════════════════════════════════════════════════════════════════════
avg_r    = df["vote_average"].mean()
top_rated = (df["vote_average"] >= 7.5).sum()

st.markdown(f"""
<div class="stats-bar">
  <div class="stat-item">
    <span class="stat-val">{len(df):,}</span>
    <span class="stat-lbl">Films Indexed</span>
  </div>
  <div class="stat-item">
    <span class="stat-val">{avg_r:.1f}</span>
    <span class="stat-lbl">Avg Rating</span>
  </div>
  <div class="stat-item">
    <span class="stat-val">{top_rated:,}</span>
    <span class="stat-lbl">Highly Rated</span>
  </div>
  <div class="stat-item">
    <span class="stat-val">TF-IDF</span>
    <span class="stat-lbl">Algorithm</span>
  </div>
  <div class="stat-item">
    <span class="stat-val">Live</span>
    <span class="stat-lbl">Data Source</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION TRIGGER
# ═══════════════════════════════════════════════════════════════════════════════
if go and selected:
    t0   = time.time()
    recs = engine.recommend(selected, top_n=top_n)
    st.session_state.recs    = recs
    st.session_state.query   = selected
    st.session_state.elapsed = time.time() - t0
elif not go and not st.session_state.recs:
    st.markdown("""
    <div class="empty-state">
      <div class="es-icon">🎞</div>
      <p>Select a film above and click <strong style="color:#c9a84c">Discover</strong> to find your next watch</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
recs = st.session_state.recs
if recs is not None and not recs.empty:
    query   = st.session_state.query
    elapsed = st.session_state.elapsed
    max_s   = recs["score"].max() or 1.0

    st.markdown(f"""
    <div class="sec-header">
      <span class="sec-title">Because you searched <span class="sec-query">{query}</span></span>
      <span class="sec-count">{len(recs)} results &nbsp;·&nbsp; {elapsed*1000:.0f}ms</span>
    </div>
    """, unsafe_allow_html=True)

    # Two-column card layout
    col_a, col_b = st.columns(2, gap="medium")
    for i, (_, row) in enumerate(recs.iterrows()):
        pct     = min(int(row["score"] / max_s * 100), 100)
        year    = str(row.get("release_date", ""))[:4] or "—"
        rating  = float(row.get("vote_average", 0))
        stars   = int(round(rating / 2))
        star_str = "★" * stars + "☆" * (5 - stars)
        genres  = str(row.get("genres", ""))
        tags_html = "".join(
            f'<span class="tag">{g.strip()}</span>'
            for g in genres.split(",")[:3] if g.strip()
        )
        overview = str(row.get("overview", ""))[:200]
        if len(str(row.get("overview", ""))) > 200:
            overview += "…"
        director = row.get("director", "")
        cast     = row.get("cast", "")
        poster   = row.get("poster_path", "")

        # Build poster HTML
        if poster:
            poster_html = f'<img src="{TMDB_IMG}{poster}" alt="{row["title"]}" loading="lazy"/>'
        else:
            poster_html = '<div class="card-poster-placeholder">🎬</div>'

        meta_parts = []
        if year and year != "—": meta_parts.append(year)
        if director: meta_parts.append(f'<b>{director}</b>')
        meta_str = " &nbsp;·&nbsp; ".join(meta_parts)

        card = f"""
        <div class="card">
          <div class="card-poster">{poster_html}</div>
          <div class="card-body">
            <div class="card-rank">{i+1:02d}</div>
            <div class="card-title">{row['title']}</div>
            <div class="card-meta">
              {meta_str}
              {"&nbsp;&nbsp;" if meta_str else ""}
              <span class="rating-badge">⭐ {rating:.1f}</span>
              &nbsp;<span class="score-stars">{star_str}</span>
            </div>
            {f'<div class="card-meta" style="color:#5a5a72;font-size:0.72rem">Cast: {cast}</div>' if cast else ''}
            <div class="card-overview">{overview}</div>
            <div class="card-tags">{tags_html}</div>
            <div class="card-score-row">
              <div class="score-track">
                <div class="score-fill" style="width:{pct}%"></div>
              </div>
              <div class="score-pct">{pct}%</div>
            </div>
          </div>
        </div>
        """
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(card, unsafe_allow_html=True)

    # ── Ornament divider ────────────────────────────────────────────────────
    st.markdown('<div class="ornament-divider">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)

    # ── Downloads & chart ───────────────────────────────────────────────────
    bot1, bot2 = st.columns([1, 2])
    with bot1:
        csv = recs[["title", "score", "vote_average", "genres"]].to_csv(index=False)
        st.download_button(
            "↓ Export as CSV",
            csv,
            f"VENDI TERA_{query.replace(' ','_')}.csv",
            "text/csv",
        )
    with bot2:
        with st.expander(" TERA Score Breakdown"):
            chart_df = recs[["title", "score"]].set_index("title")
            st.bar_chart(chart_df, color="#c9a84c")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  VENDI TERA &nbsp;·&nbsp; Powered by <em>TMDB API</em>
  &nbsp;·&nbsp; TF-IDF · Cosine Similarity · Scikit-learn · © Enla VishnuVardhan Raj
</div>
""", unsafe_allow_html=True)
