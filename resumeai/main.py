import streamlit as st
import streamlit.components.v1 as components
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── INIT SESSION STATE ───────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# ─── HANDLE NAV via query_params (no hidden buttons needed!) ───
qp = st.query_params
if "nav" in qp:
    st.session_state["page"] = qp["nav"]
    st.query_params.clear()
    st.rerun()


# ─── GLOBAL CSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── BACKGROUND ── */
.stApp {
    background: #0a0e1a !important;
    min-height: 100vh;
    position: relative;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url('coolbackgrounds-unsplash-zeller.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.15;
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(
        180deg,
        rgba(10,14,26,0.85) 0%,
        rgba(10,14,26,0.75) 50%,
        rgba(10,14,26,0.85) 100%
    );
    pointer-events: none;
    z-index: 0;
}

/* ── HIDE Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.stApp > header { display: none !important; }
.block-container {
    padding: 80px 2.5rem 4rem !important;
    max-width: 1300px !important;
    position: relative;
    z-index: 1;
}

/* ── CRITICAL: Hide the nav anchor buttons reliably ── */
[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ══════════════════════════════
   NAVBAR  — FIXED on scroll
══════════════════════════════ */
.navbar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.5rem;
    height: 62px;
    background: rgba(8,12,31,0.92);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border-bottom: 1px solid rgba(99,102,241,0.25);
    box-shadow: 0 2px 40px rgba(0,0,0,0.5);
}
.nav-links {
    display: flex; align-items: center; gap: 0.15rem;
}
.nav-link {
    padding: 0.45rem 1.05rem;
    border-radius: 10px;
    font-size: 0.84rem; font-weight: 600;
    color: rgba(255,255,255,0.55);
    cursor: pointer; transition: all 0.2s;
    border: 1px solid transparent;
    font-family: 'Plus Jakarta Sans', sans-serif;
    user-select: none;
    display: inline-block;
    text-decoration: none !important;
}
.nav-link:hover { 
    color: #fff; 
    background: rgba(255,255,255,0.09);
    text-decoration: none !important;
}
.nav-link:active,
.nav-link:focus,
.nav-link:visited {
    text-decoration: none !important;
}
.nav-link.active {
    color: #a5b4fc !important;
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.45) !important;
    text-decoration: none !important;
}
.nav-brand {
    display: flex; align-items: center; gap: 0.65rem;
    font-family: 'Syne', sans-serif;
    font-weight: 800; font-size: 1.3rem; color: #fff;
}
.nav-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 18px rgba(99,102,241,0.5);
    flex-shrink: 0;
}
.nav-status {
    display: inline-flex; align-items: center; gap: 0.45rem;
    padding: 0.38rem 1rem;
    border-radius: 99px;
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
}
.ns-on  { background: rgba(34,197,94,0.12);  border: 1px solid rgba(34,197,94,0.35);  color: #4ade80; }
.ns-off { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.35);  color: #f87171; }
.ndot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.ng { background: #22c55e; animation: glow 2s infinite; }
.nr { background: #ef4444; }
@keyframes glow { 0%,100%{box-shadow:0 0 4px #22c55e} 50%{box-shadow:0 0 14px #22c55e} }

/* ── HERO ── */
.hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
}
.hero-chip {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(236,72,153,0.12);
    border: 1px solid rgba(236,72,153,0.35);
    color: #f472b6;
    padding: 0.4rem 1.2rem;
    border-radius: 99px;
    font-size: 0.74rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.6rem, 5vw, 4rem);
    font-weight: 800; color: #fff;
    margin-bottom: 1rem; line-height: 1.08;
    letter-spacing: -0.02em;
}
.grad-text {
    background: linear-gradient(135deg, #6366f1 0%, #ec4899 45%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 200%;
    animation: gradShift 6s ease infinite;
}
@keyframes gradShift { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
.hero-sub {
    color: rgba(255,255,255,0.5);
    font-size: 1.05rem;
    max-width: 480px; margin: 0 auto 2rem;
    line-height: 1.75;
}
.api-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.45rem 1.2rem; border-radius: 99px;
    font-size: 0.78rem; font-weight: 600;
}
.ap-on  { background:rgba(34,197,94,0.1);  border:1px solid rgba(34,197,94,0.3);  color:#4ade80; }
.ap-off { background:rgba(239,68,68,0.1);  border:1px solid rgba(239,68,68,0.3);  color:#f87171; }

/* ── STATS ── */
.stat-row { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:2.5rem; }
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px; padding: 1.5rem; text-align: center;
    backdrop-filter: blur(16px); transition: all 0.3s;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg,#6366f1,#ec4899,#06b6d4);
    opacity:0; transition:opacity 0.3s;
}
.stat-card:hover { transform:translateY(-5px); border-color:rgba(99,102,241,0.4); }
.stat-card:hover::before { opacity:1; }
.stat-icon  { font-size:2rem; margin-bottom:0.5rem; }
.stat-num   { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; color:#fff; line-height:1; }
.stat-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:rgba(255,255,255,0.3); margin-top:0.4rem; }

/* ── GLASS CARD ── */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 22px; padding: 2rem;
    backdrop-filter: blur(20px); margin-bottom: 1rem;
}
.sec-hdr { display:flex; align-items:center; gap:0.85rem; margin-bottom:1.4rem; }
.sec-icon { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0; }
.ic-blue   { background:rgba(99,102,241,0.18); border:1px solid rgba(99,102,241,0.35); }
.ic-pink   { background:rgba(236,72,153,0.14); border:1px solid rgba(236,72,153,0.3); }
.ic-cyan   { background:rgba(6,182,212,0.14);  border:1px solid rgba(6,182,212,0.3); }
.sec-text { font-family:'Syne',sans-serif; font-size:1.15rem; font-weight:700; color:#fff; }
.sec-sub  { font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.15rem; }

/* ── UPLOAD ZONE ── */
.illus-zone {
    border:2px dashed rgba(99,102,241,0.4); border-radius:20px;
    padding:2rem 1.5rem; text-align:center;
    background:rgba(99,102,241,0.05); transition:all 0.3s; margin-bottom:1.25rem;
}
.illus-zone:hover { border-color:rgba(236,72,153,0.5); background:rgba(236,72,153,0.06); transform:translateY(-2px); }
.illus-title { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#e2e8f0; margin-bottom:0.3rem; }
.illus-sub   { font-size:0.78rem; color:rgba(255,255,255,0.4); margin-bottom:0.9rem; }
.fmt-wrap { display:flex; gap:0.4rem; justify-content:center; flex-wrap:wrap; }
.fmt { padding:0.22rem 0.65rem; border-radius:7px; background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3); font-size:0.68rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; }

/* ── SUCCESS INDICATOR LINE ── */
.upload-success-bar {
    height: 3px;
    background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
    border-radius: 99px;
    margin-top: 0.75rem;
    box-shadow: 0 2px 12px rgba(34, 197, 94, 0.4);
    animation: slideIn 0.4s ease-out;
}
@keyframes slideIn {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
}

/* ── IMPROVED FORM LABELS ── */
label {
    color: #a5b4fc !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
}

/* ── INPUTS ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
    background: rgba(15,23,42,0.9) !important;
    border: 2px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.92rem !important;
    caret-color: #ffffff !important;
    transition: none !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus,
.stNumberInput>div>div>input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: rgba(15,23,42,0.9) !important;
    outline: none !important;
    caret-color: #ffffff !important;
}
.stTextInput>div>div>input::placeholder,
.stTextArea>div>div>textarea::placeholder { 
    color: rgba(255,255,255,0.3) !important;
    font-style: italic !important;
}
.stSelectbox>div>div {
    background: rgba(15,23,42,0.9) !important;
    border: 2px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    transition: none !important;
}
.stSelectbox>div>div:focus-within {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
/* Remove spinner button animations */
.stNumberInput button {
    transition: none !important;
    opacity: 1 !important;
}
.stNumberInput button:hover {
    opacity: 1 !important;
    background: rgba(99,102,241,0.2) !important;
}
.stNumberInput button:active {
    opacity: 1 !important;
}

/* ── MAIN ACTION BUTTONS ── */
.stButton>button {
    width:100%!important; border-radius:12px!important;
    font-weight:700!important; padding:0.78rem 1.5rem!important;
    transition: none !important; border:none!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size: 0.95rem !important;
    opacity: 1 !important;
}
.stButton>button[kind="primary"] {
    background:linear-gradient(135deg,#6366f1,#ec4899)!important;
    color:white!important; 
    box-shadow:0 4px 24px rgba(99,102,241,0.4)!important;
    opacity: 1 !important;
}
.stButton>button[kind="primary"]:hover {
    opacity: 1 !important;
    transform: none !important;
    box-shadow:0 4px 24px rgba(99,102,241,0.4)!important;
}
.stButton>button[kind="primary"]:active {
    opacity: 1 !important;
    transform: none !important;
}
.stButton>button[kind="secondary"] {
    background:rgba(255,255,255,0.06)!important;
    border:1.5px solid rgba(255,255,255,0.14)!important;
    color:rgba(255,255,255,0.7)!important;
    opacity: 1 !important;
}
.stButton>button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.14) !important;
    opacity: 1 !important;
}
.stButton>button[kind="secondary"]:active {
    opacity: 1 !important;
}
.stFileUploader>div { 
    background:rgba(255,255,255,0.04)!important; 
    border:2px dashed rgba(99,102,241,0.35)!important; 
    border-radius:14px!important;
    transition: none !important;
    opacity: 1 !important;
}
.stFileUploader>div:hover {
    border-color: rgba(99,102,241,0.35) !important;
    background: rgba(255,255,255,0.04) !important;
    opacity: 1 !important;
}
/* File uploader main label */
.stFileUploader label {
    color: #000000 !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
}

/* Dropzone main text */
.stFileUploader section {
    color: #111111 !important;
    opacity: 1 !important;
}

/* Small helper text */
.stFileUploader section small {
    color: #555555 !important;
    opacity: 1 !important;
}

/* Dropzone styling */
.stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px;
    transition: all 0.3s ease;
    opacity: 1 !important;
}

/* Hover effect */
.stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
    border: 1px solid #6366f1 !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
    cursor: pointer;
}

/* File name */
.stFileUploader [data-testid="stFileUploaderFileName"] {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* File size */
.stFileUploader [data-testid="stFileUploaderFileSize"] {
    color: #666666 !important;
}

/* Buttons */
.stFileUploader button {
    color: #ffffff !important;
    background: #4242ff !important;
    border: none !important;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 500;
    transition: all 0.3s ease;
}

/* Button hover */
.stFileUploader button:hover {
    background: #333333 !important;
    transform: translateY(-2px);
    cursor: pointer;
}

/* Caption styling */
.stCaption {
    color: #a5b4fc !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}
/* Remove all upload animations */
.stFileUploader * {
    transition: none !important;
}
section[data-testid="stFileUploader"] {
    opacity: 1 !important;
}
section[data-testid="stFileUploader"] * {
    opacity: 1 !important;
}

/* ── BADGES ── */
.badge { display:inline-block; padding:0.28rem 0.8rem; border-radius:99px; font-size:0.72rem; font-weight:700; text-transform:uppercase; margin:0.12rem; }
.b-green { background:rgba(34,197,94,0.12);  border:1px solid rgba(34,197,94,0.35);  color:#4ade80; }
.b-amber { background:rgba(251,191,36,0.12); border:1px solid rgba(251,191,36,0.35); color:#fbbf24; }
.b-red   { background:rgba(239,68,68,0.12);  border:1px solid rgba(239,68,68,0.35);  color:#f87171; }
.b-blue  { background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.35); color:#a5b4fc; }

/* ── SUMMARY ── */
.summary-box { background:rgba(99,102,241,0.08); border-left:3px solid #6366f1; border-radius:0 10px 10px 0; padding:0.85rem 1rem; font-size:0.84rem; color:rgba(255,255,255,0.6); line-height:1.65; margin:0.6rem 0; }

/* ── RESULTS TABLE ── */
.rtable { width:100%; border-collapse:collapse; font-size:0.86rem; }
.rtable thead tr { border-bottom:2px solid rgba(99,102,241,0.2); }
.rtable th { padding:0.9rem 1rem; text-align:left; font-size:0.67rem; text-transform:uppercase; letter-spacing:0.12em; color:rgba(255,255,255,0.3); font-weight:700; }
.rtable tbody tr { border-bottom:1px solid rgba(255,255,255,0.06); transition:background 0.15s; }
.rtable tbody tr:hover { background:rgba(99,102,241,0.08); }
.rtable td { padding:0.9rem 1rem; vertical-align:middle; color:rgba(255,255,255,0.8); }
.sb-wrap { display:flex; align-items:center; gap:0.65rem; }
.sb-bg   { flex:1; height:5px; background:rgba(255,255,255,0.08); border-radius:99px; overflow:hidden; min-width:55px; }
.sb-fill { height:100%; border-radius:99px; }
.ch-m { background:rgba(34,197,94,0.12);  border:1px solid rgba(34,197,94,0.3);  color:#4ade80;  padding:0.18rem 0.5rem; border-radius:6px; font-size:0.7rem; display:inline-block; margin:0.1rem; }
.ch-x { background:rgba(239,68,68,0.12);  border:1px solid rgba(239,68,68,0.3);  color:#f87171;  padding:0.18rem 0.5rem; border-radius:6px; font-size:0.7rem; display:inline-block; margin:0.1rem; }

/* ── ABOUT & HIW pages ── */
.about-hero { text-align:center; padding:3.5rem 2rem 2rem; }
.about-title { font-family:'Syne',sans-serif; font-size:clamp(2rem,4vw,3rem); font-weight:800; color:#fff; margin-bottom:0.8rem; line-height:1.1; }
.about-sub   { color:rgba(255,255,255,0.48); font-size:1rem; max-width:500px; margin:0 auto; line-height:1.75; }
.feat-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin:2rem 0; }
.feat-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:18px; padding:1.5rem; backdrop-filter:blur(16px); transition:all 0.3s; }
.feat-card:hover { transform:translateY(-4px); border-color:rgba(99,102,241,0.35); background:rgba(99,102,241,0.07); }
.feat-icon  { font-size:2rem; margin-bottom:0.75rem; }
.feat-title { font-family:'Syne',sans-serif; font-size:0.95rem; font-weight:700; color:#e2e8f0; margin-bottom:0.45rem; }
.feat-desc  { font-size:0.8rem; color:rgba(255,255,255,0.42); line-height:1.65; }
.impact-row { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:1.5rem 0; }
.impact-card { background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(236,72,153,0.08)); border:1px solid rgba(99,102,241,0.28); border-radius:16px; padding:1.5rem; text-align:center; transition:all 0.3s; }
.impact-card:hover { transform:scale(1.04); }
.impact-num { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; background:linear-gradient(135deg,#6366f1,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:0.3rem; }
.impact-lbl { font-size:0.73rem; color:rgba(255,255,255,0.45); font-weight:600; text-transform:uppercase; letter-spacing:0.08em; }
.hiw-step { display:flex; gap:1.25rem; align-items:flex-start; padding:1.5rem; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:18px; margin-bottom:0.85rem; transition:all 0.3s; }
.hiw-step:hover { border-color:rgba(99,102,241,0.35); background:rgba(99,102,241,0.07); transform:translateX(4px); }
.hiw-num { width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg,#6366f1,#ec4899); display:flex; align-items:center; justify-content:center; font-family:'Syne',sans-serif; font-weight:800; font-size:1.1rem; color:#fff; flex-shrink:0; box-shadow:0 4px 16px rgba(99,102,241,0.4); }
.hiw-title { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#e2e8f0; margin-bottom:0.4rem; }
.hiw-desc  { font-size:0.82rem; color:rgba(255,255,255,0.45); line-height:1.65; }
.hiw-connector { width:2px; height:28px; background:linear-gradient(180deg,rgba(99,102,241,0.5),transparent); margin:0 0 0 21px; }
.tech-badge { display:inline-flex; align-items:center; gap:0.4rem; padding:0.4rem 0.9rem; border-radius:10px; font-size:0.75rem; font-weight:700; margin:0.3rem; }
.tb-indigo { background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35); color:#a5b4fc; }
.tb-pink   { background:rgba(236,72,153,0.12); border:1px solid rgba(236,72,153,0.3);  color:#f9a8d4; }
.tb-cyan   { background:rgba(6,182,212,0.12);  border:1px solid rgba(6,182,212,0.3);   color:#67e8f9; }
.tb-green  { background:rgba(34,197,94,0.12);  border:1px solid rgba(34,197,94,0.3);   color:#86efac; }
.div-line { height:1px; background:linear-gradient(90deg,transparent,rgba(99,102,241,0.4),rgba(236,72,153,0.3),transparent); margin:2rem 0; }

[data-testid="metric-container"] { background:rgba(255,255,255,0.04)!important; border:1px solid rgba(255,255,255,0.09)!important; border-radius:12px!important; padding:1rem!important; }
[data-testid="stMetricValue"] { color:#e2e8f0!important; font-family:'Syne',sans-serif!important; }
[data-testid="stMetricLabel"] { color:rgba(255,255,255,0.4)!important; }
.stProgress>div>div { background:linear-gradient(90deg,#6366f1,#ec4899)!important; border-radius:99px!important; }
hr { border-color:rgba(255,255,255,0.08)!important; margin:2rem 0!important; }
.streamlit-expanderHeader { background:rgba(255,255,255,0.04)!important; color:#e2e8f0!important; border-radius:10px!important; border:1px solid rgba(255,255,255,0.08)!important; }
.streamlit-expanderContent { background:rgba(255,255,255,0.02)!important; border:1px solid rgba(255,255,255,0.06)!important; border-top:none!important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────
def api_get(path):
    try: return requests.get(f"{API_URL}{path}", timeout=5).json()
    except: return {}

def api_post(path, **kw):
    try: return requests.post(f"{API_URL}{path}", timeout=60, **kw).json()
    except Exception as e: return {"error": str(e)}

def sc(s): return "#4ade80" if s >= 75 else "#fbbf24" if s >= 50 else "#f87171"

def rbadge(rec):
    cls = "b-green" if rec == "SHORTLIST" else "b-amber" if rec == "MAYBE" else "b-red"
    em  = "✓" if rec == "SHORTLIST" else "~" if rec == "MAYBE" else "✗"
    return f'<span class="badge {cls}">{em} {rec}</span>'


# ─── API STATUS ───────────────────────────────────────
api_data = api_get("/")
online   = bool(api_data.get("status"))


# ══════════════════════════════════════════════════════
#  FIXED NAVBAR — uses JS to set query_params for nav
#  (NO hidden Streamlit buttons that bleed into page!)
# ══════════════════════════════════════════════════════
page   = st.session_state["page"]
ns_cls = "ns-on"  if online else "ns-off"
nd_cls = "ng"     if online else "nr"
ns_txt = "LIVE"   if online else "OFFLINE"

def _lc(p): return "nav-link active" if page == p else "nav-link"

# Pure HTML navbar — clicking a link adds ?nav=xxx to the URL
# Streamlit detects the query param change and reruns → page switches
st.markdown(f"""
<div class="navbar">
    <div class="nav-brand">
        <div class="nav-logo">🎯</div>
        ResumeAI
    </div>
    <div class="nav-links">
        <a class="{_lc('home')}"  href="?nav=home"  target="_self">🏠 Home</a>
        <a class="{_lc('about')}" href="?nav=about" target="_self">📄 About</a>
        <a class="{_lc('hiw')}"   href="?nav=hiw"   target="_self">⚙️ How It Works</a>
    </div>
    <div class="nav-status {ns_cls}">
        <span class="ndot {nd_cls}"></span>
        {ns_txt}
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  PAGE: ABOUT
# ═══════════════════════════════════════════════════════
if page == "about":
    st.markdown("""
    <div class="about-hero">
        <div class="hero-chip">✦ About the Platform</div>
        <h1 class="about-title">Resume <span class="grad-text">Screening AI</span></h1>
        <p class="about-sub">
            An intelligent recruitment assistant automating candidate evaluation
            using state-of-the-art AI — helping HR teams find top talent in seconds.
        </p>
    </div>
    <div class="div-line"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
        <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:0.9rem;">
            📌 What is Resume Screening AI?
        </div>
        <p style="color:rgba(255,255,255,0.52);font-size:0.88rem;line-height:1.85;">
            Resume Screening AI is an intelligent recruitment assistant designed to automate and optimize the
            candidate evaluation process. It leverages advanced AI models to extract, analyze, and match resume
            content against job descriptions — helping HR teams identify top candidates quickly and accurately.
            Built on <strong style="color:#a5b4fc;">LLaMA 3 via Groq API</strong>, it delivers ultra-fast
            inference with enterprise-grade accuracy.
        </p>
    </div>

    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin:1.5rem 0 1rem;">
        ✨ Key Features
    </div>
    <div class="feat-grid">
        <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">OCR Support</div><div class="feat-desc">Processes scanned resumes and PDFs with high accuracy using advanced optical character recognition.</div></div>
        <div class="feat-card"><div class="feat-icon">🧠</div><div class="feat-title">Semantic Matching</div><div class="feat-desc">Uses modern embedding models to semantically compare skills, experience, and education with job requirements.</div></div>
        <div class="feat-card"><div class="feat-icon">📊</div><div class="feat-title">Automated Scoring</div><div class="feat-desc">Provides a structured match score (0–100) along with detailed reasoning for each candidate.</div></div>
        <div class="feat-card"><div class="feat-icon">⚡</div><div class="feat-title">Fast & Scalable</div><div class="feat-desc">Powered by LLaMA 3 via Groq API — screen hundreds of resumes in minutes, not hours.</div></div>
        <div class="feat-card"><div class="feat-icon">🗂️</div><div class="feat-title">ATS-Friendly Output</div><div class="feat-desc">Generates structured JSON or PDF resumes ready for Applicant Tracking Systems.</div></div>
        <div class="feat-card"><div class="feat-icon">🎯</div><div class="feat-title">Smart Ranking</div><div class="feat-desc">Automatically categorizes candidates into SHORTLIST, MAYBE, and REJECT with explainable AI reasoning.</div></div>
    </div>
    <div class="div-line"></div>
    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">📈 Impact</div>
    <div class="impact-row">
        <div class="impact-card"><div class="impact-num">80%</div><div class="impact-lbl">Reduction in Manual Screening Time</div></div>
        <div class="impact-card"><div class="impact-num">3×</div><div class="impact-lbl">Improvement in Hiring Accuracy</div></div>
        <div class="impact-card"><div class="impact-num">100%</div><div class="impact-lbl">Standardized Evaluation Process</div></div>
    </div>
    <div class="div-line"></div>
    <div style="text-align:center;padding:0.5rem 0 1rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.78rem;color:rgba(255,255,255,0.18);letter-spacing:0.12em;">
            BUILT WITH ⚡ GROQ · LLAMA 3 · STREAMLIT · PYTHON · FASTAPI
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════
#  PAGE: HOW IT WORKS
# ═══════════════════════════════════════════════════════
if page == "hiw":
    st.markdown("""
    <div class="about-hero">
        <div class="hero-chip">✦ Step-by-Step Guide</div>
        <h1 class="about-title">How It <span class="grad-text">Works</span></h1>
        <p class="about-sub">
            From job description to ranked candidates — our AI pipeline handles
            everything in seconds using Groq-powered LLaMA 3.
        </p>
    </div>
    <div class="div-line"></div>

    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1.25rem;">
        🚀 The Pipeline
    </div>

    <div class="hiw-step">
        <div class="hiw-num">1</div>
        <div><div class="hiw-title">📋 Upload Job Description</div>
        <div class="hiw-desc">Enter the job title, description, required skills, min experience, and education level. The system extracts key requirements and stores them as a structured profile for matching.</div></div>
    </div>
    <div class="hiw-connector"></div>
    <div class="hiw-step">
        <div class="hiw-num">2</div>
        <div><div class="hiw-title">📂 Upload Resumes</div>
        <div class="hiw-desc">Upload one or multiple resumes in PDF, DOCX, DOC, or TXT format. The backend extracts text using OCR and document parsers, converting every resume into structured data.</div></div>
    </div>
    <div class="hiw-connector"></div>
    <div class="hiw-step">
        <div class="hiw-num">3</div>
        <div><div class="hiw-title">🧠 AI Extraction via LLaMA 3</div>
        <div class="hiw-desc">Each resume is sent to LLaMA 3 (via Groq API) which extracts candidate name, skills, years of experience, education, and a professional summary — all in structured JSON.</div></div>
    </div>
    <div class="hiw-connector"></div>
    <div class="hiw-step">
        <div class="hiw-num">4</div>
        <div><div class="hiw-title">🎯 Semantic Matching & Scoring</div>
        <div class="hiw-desc">The AI compares each candidate profile against the job description. It calculates a <strong style="color:#a5b4fc;">match score (0–100)</strong> based on skill overlap, experience relevance, and education fit — with full reasoning.</div></div>
    </div>
    <div class="hiw-connector"></div>
    <div class="hiw-step">
        <div class="hiw-num">5</div>
        <div><div class="hiw-title">📊 Ranking & Recommendation</div>
        <div class="hiw-desc">Candidates are automatically sorted by score and labeled as <strong style="color:#4ade80;">SHORTLIST</strong>, <strong style="color:#fbbf24;">MAYBE</strong>, or <strong style="color:#f87171;">REJECT</strong>. A full breakdown of matched vs missing skills is shown for every candidate.</div></div>
    </div>
    <div class="hiw-connector"></div>
    <div class="hiw-step">
        <div class="hiw-num">6</div>
        <div><div class="hiw-title">⚡ Instant Results</div>
        <div class="hiw-desc">Results appear in real-time with a filterable table and expandable detailed views. Groq's ultra-fast inference means even large batches complete in seconds — not minutes.</div></div>
    </div>

    <div class="div-line"></div>
    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">🛠️ Tech Stack</div>
    <div style="display:flex;flex-wrap:wrap;gap:0.25rem;margin-bottom:2rem;">
        <span class="tech-badge tb-indigo">⚡ Groq API</span>
        <span class="tech-badge tb-pink">🦙 LLaMA 3</span>
        <span class="tech-badge tb-cyan">🌐 Streamlit</span>
        <span class="tech-badge tb-green">🐍 Python</span>
        <span class="tech-badge tb-indigo">🚀 FastAPI</span>
        <span class="tech-badge tb-pink">📄 PyMuPDF</span>
        <span class="tech-badge tb-cyan">🔍 OCR</span>
        <span class="tech-badge tb-green">📊 JSON Schema</span>
    </div>
    <div class="glass" style="text-align:center;padding:1.5rem;">
        <div style="font-size:2rem;margin-bottom:0.75rem;">🎯</div>
        <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:0.5rem;">Ready to get started?</div>
        <div style="font-size:0.83rem;color:rgba(255,255,255,0.4);">Head to the <a href="?nav=home" target="_self" style="color:#a5b4fc;text-decoration:none;font-weight:700;">Home</a> tab, upload a job description and resumes, then hit Score & Rank!</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════
resumes_n   = api_data.get("resumes_uploaded", 0)
jd_display  = api_data.get("jd_title", "None") or "No Job Active"
shortlisted = st.session_state.get("shortlisted", 0)

# HERO
ap_cls = "ap-on"  if online else "ap-off"
ap_dot = "ng" if online else "nr"
ap_txt = "API Ready · " + api_data.get("model","") if online else "⚠️ Backend offline — start with: uvicorn backend:fapp --port 8000"

st.markdown(f"""
<div class="hero">
    <div class="hero-chip">✦ AI-Powered Recruitment Platform</div>
    <h1 class="hero-title">Resume <span class="grad-text">Screening AI</span></h1>
    <p class="hero-sub">Powered by <strong>Groq ⚡ LLaMA 3</strong> — ultra-fast AI candidate scoring</p>
    <div style="display:flex;justify-content:center;">
        <div class="api-pill {ap_cls}">
            <span class="ndot {ap_dot}"></span>
            {ap_txt}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# STATS
st.markdown(f"""
<div class="stat-row">
    <div class="stat-card"><div class="stat-icon">📄</div><div class="stat-num">{resumes_n}</div><div class="stat-label">Resumes Uploaded</div></div>
    <div class="stat-card"><div class="stat-icon">💼</div><div class="stat-num" style="font-size:1rem;padding-top:.5rem;">{jd_display}</div><div class="stat-label">Active Job</div></div>
    <div class="stat-card"><div class="stat-icon">✅</div><div class="stat-num">{shortlisted}</div><div class="stat-label">Shortlisted</div></div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="glass"><div class="sec-hdr"><div class="sec-icon ic-blue">📋</div><div><div class="sec-text">Job Description</div><div class="sec-sub">Define the role you are hiring for</div></div></div></div>', unsafe_allow_html=True)
    jd_title  = st.text_input("Job Title", placeholder="e.g. Senior Python Developer")
    jd_desc   = st.text_area("Description", placeholder="Describe the role and requirements...", height=115)
    jd_skills = st.text_input("Required Skills", placeholder="python, django, docker, git")
    c1, c2 = st.columns(2)
    with c1: jd_exp = st.number_input("Min Experience (years)", min_value=0, max_value=20, value=0)
    with c2: jd_edu = st.selectbox("Education Level", ["not specified","diploma","associate","bachelors","masters","phd"])
    if st.button("📤 Upload Job Description", type="primary"):
        if not jd_title or not jd_desc:
            st.error("⚠️ Job title and description are required!")
        else:
            with st.spinner("Uploading job description..."):
                res = api_post("/upload-jd", json={
                    "title": jd_title, "description": jd_desc,
                    "skills_required": [s.strip() for s in jd_skills.split(",") if s.strip()],
                    "experience_years": jd_exp if jd_exp > 0 else None, "education": jd_edu
                })
            if res.get("jd_id"): 
                st.success(f"✓ Successfully uploaded: **{jd_title}**")
                st.markdown('<div class="upload-success-bar"></div>', unsafe_allow_html=True)
                st.rerun()
            else: st.error(res.get("error","Upload failed"))

with right:
    st.markdown('<div class="sec-hdr"><div class="sec-icon ic-pink">📂</div><div><div class="sec-text">Upload Resumes</div><div class="sec-sub">Groq AI scores instantly ⚡</div></div></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="illus-zone">
        <div style="font-size:4rem;margin-bottom:0.5rem;filter:drop-shadow(0 8px 24px rgba(99,102,241,0.6));">📄</div>
        <div class="illus-title">Drop your resume files here</div>
        <div class="illus-sub">LLaMA 3 extracts skills & scores in seconds</div>
        <div class="fmt-wrap">
            <span class="fmt">PDF</span><span class="fmt">DOCX</span>
            <span class="fmt">DOC</span><span class="fmt">TXT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    files = st.file_uploader("Upload Resumes", type=["pdf","docx","doc","txt"],
                             accept_multiple_files=True, label_visibility="collapsed")
    if files:
        st.caption(f"📎 {len(files)} file(s) ready to upload")
        if st.button("📤 Upload All Resumes", type="primary"):
            prog = st.progress(0)
            upload_count = 0
            for i, f in enumerate(files):
                with st.spinner(f"Uploading {f.name}..."):
                    f.seek(0)
                    res = api_post("/upload-resume",
                                   files={"file": (f.name, f.read(), "application/octet-stream")})
                if res.get("resume_id"):
                    p = res.get("parsed",); 
                    st.success(f"✅ {p.get('name', f.name)}")
                    upload_count += 1
                else: st.error(f"❌ {f.name}: {res.get('error','Failed')}")
                prog.progress((i+1)/len(files))
            if upload_count > 0:
                st.markdown('<div class="upload-success-bar"></div>', unsafe_allow_html=True)
            st.rerun()

st.divider()
cs, cc = st.columns([5, 1])
with cs: score_btn = st.button("⚡ Score & Rank with Groq LLaMA 3", type="primary")
with cc:
    if st.button("🗑️ Clear", type="secondary"):
        try: requests.delete(f"{API_URL}/clear", timeout=5)
        except: pass
        st.session_state.clear(); st.rerun()

if score_btn:
    with st.spinner("⚡ Groq LLaMA 3 ranking candidates..."):
        data = api_get("/ranked-candidates")
    if data.get("error"):    st.error(data["error"])
    elif data.get("detail"): st.warning(data["detail"])
    else:
        st.session_state["results"]     = data
        st.session_state["shortlisted"] = data.get("shortlisted", 0)
        st.rerun()

if "results" in st.session_state:
    data       = st.session_state["results"]
    candidates = data.get("ranked_candidates", [])
    if candidates:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#fff;margin-bottom:1rem;">📊 Ranked Candidates</div>
        <div style="display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1.5rem;">
            <span class="badge b-blue">Total: {data['total_candidates']}</span>
            <span class="badge b-green">Shortlist: {data['shortlisted']}</span>
            <span class="badge b-amber">Maybe: {data['maybe']}</span>
            <span class="badge b-red">Reject: {data['rejected']}</span>
        </div>""", unsafe_allow_html=True)

        f_opt    = st.radio("Filter:", ["All","SHORTLIST","MAYBE","REJECT"], horizontal=True)
        filtered = candidates if f_opt == "All" else [c for c in candidates if c["recommendation"] == f_opt]
        rows = ""
        for i, c in enumerate(filtered):
            s = c.get("final_score",0); color = sc(s)
            mp = ", ".join(c.get("matched_skills",[])[:3]) or "None"
            if len(c.get("matched_skills",[])) > 3: mp += f" +{len(c['matched_skills'])-3}"
            rows += f"""<tr>
                <td style="color:rgba(255,255,255,0.3);font-weight:700;">{i+1}</td>
                <td><div style="font-weight:600;color:#e2e8f0;">{c.get('candidate_name','Unknown')}</div><div style="font-size:.7rem;color:rgba(255,255,255,.3);">{c.get('filename','')}</div></td>
                <td><div class="sb-wrap"><div class="sb-bg"><div class="sb-fill" style="width:{s}%;background:{color};"></div></div><span style="font-weight:700;color:{color};min-width:34px;">{s}</span></div></td>
                <td style="font-size:.78rem;color:rgba(255,255,255,.6);">{mp}</td>
                <td style="font-size:.78rem;color:rgba(255,255,255,.5);">{c.get('experience_years','N/A')} yrs</td>
                <td><span class="badge b-blue">{c.get('education','N/A')}</span></td>
                <td>{rbadge(c.get('recommendation',''))}</td>
            </tr>"""
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:18px;overflow:hidden;backdrop-filter:blur(20px);">
        <table class="rtable"><thead><tr><th>#</th><th>Candidate</th><th>Score</th><th>Top Skills</th><th>Experience</th><th>Education</th><th>Status</th></tr></thead>
        <tbody>{rows}</tbody></table></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.15rem;font-weight:700;color:#e2e8f0;margin-bottom:.85rem;">🔍 Detailed Breakdown</div>', unsafe_allow_html=True)
        for c in filtered:
            rec   = c.get("recommendation","")
            emoji = "✅" if rec == "SHORTLIST" else "⚠️" if rec == "MAYBE" else "❌"
            with st.expander(f"{emoji}  {c.get('candidate_name','Unknown')}  —  {c.get('final_score',0)}/100  ({rec})"):
                m1,m2,m3 = st.columns(3)
                m1.metric("Final Score", f"{c.get('final_score',0)}/100")
                m2.metric("Experience",  f"{c.get('experience_years','N/A')} yrs")
                m3.metric("Education",   c.get("education","N/A").title())
                if c.get("summary"):
                    st.markdown(f'<div class="summary-box">💬 {c["summary"]}</div>', unsafe_allow_html=True)
                cm, cx = st.columns(2)
                with cm:
                    st.markdown("**✅ Matched Skills**")
                    matched = c.get("matched_skills",[])
                    st.markdown(" ".join([f'<span class="ch-m">{s}</span>' for s in matched]) if matched else "None", unsafe_allow_html=True)
                with cx:
                    st.markdown("**❌ Missing Skills**")
                    missing = c.get("missing_skills",[])
                    st.markdown(" ".join([f'<span class="ch-x">{s}</span>' for s in missing]) if missing else "None", unsafe_allow_html=True)