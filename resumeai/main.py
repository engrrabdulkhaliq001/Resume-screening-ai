import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ResumeAI — AI-Powered Recruitment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state["page"] = "home"

qp = st.query_params
if "nav" in qp:
    st.session_state["page"] = qp["nav"]
    st.query_params.clear()
    st.rerun()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg-deep:   #050914;
    --bg-mid:    #080f20;
    --bg-card:   rgba(255,255,255,0.04);
    --bg-card-h: rgba(255,255,255,0.07);
    --border:    rgba(255,255,255,0.08);
    --border-g:  rgba(99,179,237,0.25);
    --primary:   #3b82f6;
    --primary-g: rgba(59,130,246,0.4);
    --accent:    #8b5cf6;
    --accent-g:  rgba(139,92,246,0.35);
    --cyan:      #06b6d4;
    --text-hi:   #f0f6ff;
    --text-mid:  #94a3b8;
    --text-lo:   #475569;
    --green:     #22c55e;
    --yellow:    #f59e0b;
    --red:       #ef4444;
    --r-sm: 8px; --r-md: 14px; --r-lg: 20px; --r-xl: 28px;
    --font-d: 'Syne', sans-serif;
    --font-b: 'DM Sans', sans-serif;
    --tr: 0.3s cubic-bezier(0.4,0,0.2,1);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: var(--font-b) !important; }

/* ── BACKGROUND: image with opacity, no flash ── */
html {
    /* Set bg on html so it loads instantly before JS */
    background: #050914 !important;
}

html, body {
    background-color: #050914 !important;
    min-height: 100vh;
}

.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
section[data-testid="stSidebar"],
.main, .main > div {
    background: transparent !important;
    background-color: transparent !important;
}

/* BG image layer on stApp itself — loads with page, no extra request delay */
.stApp {
    color: var(--text-hi) !important;
    min-height: 100vh;
    position: relative;
    background-color: #050914 !important;
}

/* Background image with opacity via pseudo-element */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url('https://raw.githubusercontent.com/engrrabdulkhaliq001/Resume-screening-ai/main/background.png');
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    opacity: 0.45;
    pointer-events: none;
    z-index: 0;
}

/* Subtle dark overlay so text stays readable */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background: rgba(5,9,20,0.45);
    pointer-events: none;
    z-index: 0;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stApp > header { display: none !important; }
.block-container {
    padding: 70px 2rem 4rem !important;
    max-width: 1280px !important;
    position: relative; z-index: 1;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-mid); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ════════════════ NAVBAR (from index_fixed .glass-nav) ═══════════════ */
.navbar {
    position: fixed !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    z-index: 999999 !important;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 2.5rem; height: 60px;
    background: rgba(5,9,20,0.7);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-bottom: 1px solid var(--border);
    box-shadow: 0 2px 32px rgba(0,0,0,0.4);
}
.nav-brand {
    display: flex; align-items: center; gap: 10px;
    text-decoration: none !important;
}
.nav-brand-icon { font-size: 1.5rem; filter: drop-shadow(0 0 10px var(--primary-g)); }
.nav-brand-text {
    font-family: var(--font-d); font-weight: 800; font-size: 1.25rem;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; letter-spacing: -0.02em;
}
.nav-links { display: flex; align-items: center; gap: 4px; }
.nav-link {
    font-family: var(--font-d); font-weight: 500; font-size: 0.9rem;
    color: var(--text-mid) !important;
    padding: 8px 16px !important; border-radius: var(--r-sm);
    transition: var(--tr); letter-spacing: 0.02em;
    position: relative; text-decoration: none !important; display: inline-block;
}
.nav-link:hover { color: var(--text-hi) !important; background: var(--bg-card); text-decoration: none !important; }
.nav-link.active { color: var(--text-hi) !important; background: var(--bg-card); }
.nav-link.active::after {
    content: ''; position: absolute; bottom: 4px; left: 50%;
    transform: translateX(-50%); width: 18px; height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--accent)); border-radius: 2px;
}

/* ── HAMBURGER LABEL — mobile only, pure CSS toggle ── */
.hamburger {
    display: none !important;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 5px;
    width: 40px; height: 40px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    cursor: pointer;
    padding: 8px;
    transition: background 0.2s;
    flex-shrink: 0;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
}
.hamburger:hover { background: rgba(255,255,255,0.18); }
.hamburger span {
    display: block;
    width: 20px; height: 2px;
    background: #ffffff;
    border-radius: 2px;
    transition: all 0.3s ease;
    transform-origin: center;
    pointer-events: none;
}

/* X when checkbox checked */
#menuToggle:checked + .mobile-menu { display: flex !important; }
#menuToggle:checked ~ * .hamburger span:nth-child(1),
label[for="menuToggle"]:has(~ #menuToggle:checked) span:nth-child(1) { transform: translateY(7px) rotate(45deg); }

/* ── MOBILE DROPDOWN MENU ── */
.mobile-menu {
    display: none;
    position: fixed;
    top: 60px; left: 0; right: 0;
    z-index: 999998;
    background: rgba(5,9,20,0.97);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    flex-direction: column;
    padding: 0.75rem 1rem;
    gap: 0.25rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    animation: slideDown 0.25s ease;
}
#menuToggle:checked + .mobile-menu {
    display: flex !important;
}
.mobile-menu a {
    font-family: var(--font-d);
    font-weight: 600; font-size: 0.95rem;
    color: rgba(255,255,255,0.75) !important;
    padding: 0.85rem 1rem;
    border-radius: 10px;
    text-decoration: none !important;
    transition: background 0.2s, color 0.2s;
    border: 1px solid transparent;
    display: block;
}
.mobile-menu a:hover {
    background: rgba(255,255,255,0.08);
    color: #ffffff !important;
}
.mobile-menu a.active {
    background: rgba(59,130,246,0.15);
    border-color: rgba(59,130,246,0.3);
    color: #93c5fd !important;
}
@keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.status-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3);
    padding: 5px 12px; border-radius: 50px;
    font-size: 0.7rem; font-family: var(--font-d); font-weight: 700; letter-spacing: 0.08em;
}
.status-badge.online { background: rgba(34,197,94,0.12); border-color: rgba(34,197,94,0.3); color: #4ade80; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--red); display: inline-block; animation: pulseDot 2s infinite; }
.status-badge.online .status-dot { background: #22c55e; }
.status-text { color: var(--red); }
.status-badge.online .status-text { color: #4ade80; }

/* ════════════════ HERO (orbs, grid, badge, heading) ═══════════════ */
.hero-section {
    position: relative; padding: 80px 0 60px;
    text-align: center; overflow: hidden;
}
.hero-bg-grid {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(59,130,246,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.05) 1px, transparent 1px);
    background-size: 60px 60px;
    -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black, transparent);
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black, transparent);
}
.hero-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
.orb-1 { width: 500px; height: 500px; background: rgba(59,130,246,0.15); top: -150px; left: -100px; }
.orb-2 { width: 400px; height: 400px; background: rgba(139,92,246,0.12); bottom: -100px; right: -50px; }
.orb-3 { width: 300px; height: 300px; background: rgba(6,182,212,0.08); top: 50%; left: 50%; transform: translate(-50%,-50%); }
.hero-content { position: relative; z-index: 1; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.4);
    color: #ffffff; padding: 6px 18px; border-radius: 50px;
    font-size: 0.78rem; font-family: var(--font-d); font-weight: 600;
    letter-spacing: 0.08em; margin-bottom: 24px;
    animation: fadeUp 0.6s ease both;
}
.hero-heading {
    font-family: var(--font-d); font-weight: 800;
    font-size: clamp(1.8rem, 4vw, 3rem);
    line-height: 1.1; letter-spacing: -0.02em;
    color: var(--text-hi); margin-bottom: 20px;
    animation: fadeUp 0.7s 0.1s ease both;
}
.gradient-text {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #67e8f9 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: #ffffff; font-size: 1.05rem; font-weight: 300;
    margin-bottom: 28px; animation: fadeUp 0.7s 0.2s ease both;
}
.api-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 18px; border-radius: 50px; font-size: 0.85rem;
    animation: fadeUp 0.7s 0.3s ease both;
}
.api-pill.on  { background: rgba(34,197,94,0.10); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }
.api-pill.off { background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.3); color: #fcd34d; }
.ndot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; animation: pulseDot 2s infinite; }
.ndot.g { background: #22c55e; }
.ndot.y { background: #f59e0b; }

/* ════════════════ STAT CARDS ═══════════════ */
.stats-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin-bottom: 2.5rem; }
.stat-card {
    display: flex; align-items: center; gap: 20px;
    padding: 28px 32px; background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-xl); backdrop-filter: blur(12px);
    overflow: visible; /* NEVER overflow:hidden — that breaks clicks */
    transition: var(--tr);
}
.stat-card:hover { transform: translateY(-4px); border-color: var(--border-g); }
.stat-icon { font-size: 2.2rem; flex-shrink: 0; filter: drop-shadow(0 0 12px var(--primary-g)); }
.stat-value {
    font-family: var(--font-d); font-weight: 800; font-size: 2rem;
    background: linear-gradient(135deg, var(--text-hi), #93c5fd);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; line-height: 1;
}
.stat-value-sm { font-size: 1.05rem; word-break: break-word; }
.stat-label { font-size: 0.8rem; color: var(--text-lo); font-weight: 500; margin-top: 4px; letter-spacing: 0.04em; text-transform: uppercase; }

/* ════════════════ GLASS CARDS ═══════════════
   overflow: visible — this is THE critical fix.
   overflow:hidden + backdrop-filter = chrome bug
   that silently swallows all click events.
══════════════════════════════════════════════ */
.glass-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-xl);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    overflow: visible;
    transition: var(--tr); margin-bottom: 8px;
}
.glass-card:hover { border-color: var(--border-g); background: var(--bg-card-h); }
.card-hdr { padding: 28px 32px 0; }
.card-body { padding: 16px 32px 24px; }
.card-div { height: 1px; background: var(--border); margin: 14px 0; }
.sec-title { font-family: var(--font-d); font-weight: 700; font-size: 1.3rem; color: #ffffff; margin-bottom: 4px; text-shadow: 0 1px 8px rgba(0,0,0,0.9); }
.sec-sub   { color: var(--text-mid); font-size: 0.85rem; }
.sec-row   { display: flex; align-items: center; gap: 12px; }
.sec-ico   { font-size: 1.5rem; }

/* ════════════════ FORM INPUTS ═══════════════ */
label {
    display: block !important;
    font-size: 0.8rem !important; font-weight: 700 !important;
    color: #ffffff !important; margin-bottom: 8px !important;
    letter-spacing: 0.04em !important; text-transform: uppercase !important;
    font-family: var(--font-d) !important;
    text-shadow: 0 1px 6px rgba(0,0,0,0.9) !important;
}
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stNumberInput > div > div > input {
    background: #000000 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-hi) !important;
    padding: 12px 16px !important;
    font-family: var(--font-b) !important; font-size: 0.9rem !important;
    caret-color: #ffffff !important; outline: none !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(59,130,246,0.5) !important;
    background: #000000 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    caret-color: #ffffff !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea  > div > div > textarea::placeholder { color: var(--text-lo) !important; }
.stSelectbox > div > div {
    background: #000000 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important; color: var(--text-hi) !important;
}
.stSelectbox > div > div > div { color: var(--text-hi) !important; }
.stSelectbox svg { color: var(--text-mid) !important; }

/* ════════════════ BUTTONS ═══════════════
   NO pointer-events or disabled attribute
   manipulation — that is what broke them.
   Only visual CSS, Streamlit handles events.
══════════════════════════════════════════ */
.stButton > button {
    width: 100% !important;
    display: flex !important;
    align-items: center !important; justify-content: center !important;
    gap: 8px !important;
    font-family: var(--font-d) !important; font-weight: 600 !important;
    font-size: 0.9rem !important; letter-spacing: 0.02em !important;
    padding: 13px 24px !important; border-radius: var(--r-md) !important;
    cursor: pointer !important; border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 30px rgba(59,130,246,0.55) !important;
    filter: brightness(1.06) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(239,68,68,0.10) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    color: #fca5a5 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(239,68,68,0.18) !important;
    border-color: rgba(239,68,68,0.4) !important;
}

/* ════════════════ FILE UPLOADER ═══════════════ */
.stFileUploader > div {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--r-lg) !important; transition: var(--tr) !important;
}
.stFileUploader > div:hover {
    border-color: rgba(59,130,246,0.5) !important;
    background: rgba(59,130,246,0.05) !important;
}
section[data-testid="stFileUploader"] small { color: var(--text-lo) !important; }
section[data-testid="stFileUploader"] span  { color: var(--text-mid) !important; }

/* ── BROWSE FILES BUTTON — black bg, white text, purple hover ── */
[data-testid="stFileUploaderDropzone"] button,
.stFileUploader button,
button[data-testid="stBaseButton-secondary"][aria-label=""] {
    background: #000000 !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.6) !important;
    width: auto !important;
    transition: background 0.25s, border-color 0.25s, box-shadow 0.25s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
.stFileUploader button:hover,
button[data-testid="stBaseButton-secondary"][aria-label=""]:hover {
    background: #1a1a2e !important;
    border-color: rgba(99,102,241,0.8) !important;
    box-shadow: 0 4px 22px rgba(99,102,241,0.45) !important;
    color: #ffffff !important;
}
.illus-zone {
    border: 2px dashed var(--border); border-radius: var(--r-lg);
    padding: 36px 20px; text-align: center;
    background: rgba(255,255,255,0.02); transition: var(--tr); margin-bottom: 12px;
}
.illus-zone:hover { border-color: rgba(59,130,246,0.5); background: rgba(59,130,246,0.05); }
.illus-icon  { font-size: 2.5rem; margin-bottom: 10px; }
.illus-title { font-family: var(--font-d); font-weight: 600; font-size: 1rem; color: var(--text-hi); margin-bottom: 4px; }
.illus-sub   { color: var(--text-mid); font-size: 0.85rem; margin-bottom: 10px; }
.fmt-wrap { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }
.fmt {
    padding: 3px 10px; border-radius: 5px;
    background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25);
    font-size: 0.72rem; font-weight: 600; color: #93c5fd; text-transform: uppercase; letter-spacing: 0.06em;
}

/* ════════════════ RESULTS ═══════════════ */
.badge {
    display: inline-block; padding: 4px 12px; border-radius: 50px;
    font-family: var(--font-d); font-weight: 700;
    font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; margin: 2px;
}
.b-green { background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }
.b-amber { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3); color: #fbbf24; }
.b-red   { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.3);  color: #f87171; }
.b-blue  { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3); color: #93c5fd; }
.rtable { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
.rtable thead tr { border-bottom: 1px solid var(--border); }
.rtable th { padding: 14px 18px; text-align: left; font-family: var(--font-d); font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-lo); white-space: nowrap; }
.rtable tbody tr { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background .15s; }
.rtable tbody tr:hover td { background: rgba(59,130,246,0.04); }
.rtable td { padding: 14px 18px; vertical-align: top; }
.cname  { font-weight: 500; color: var(--text-hi); font-size: .9rem; }
.cfname { font-size: .72rem; color: var(--text-lo); margin-top: 2px; }
.sb-wrap { display: flex; align-items: center; gap: 10px; }
.sb-val  { font-family: var(--font-d); font-weight: 700; font-size: 1rem; min-width: 32px; }
.sb-bg   { width: 80px; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.sb-fill { height: 100%; border-radius: 3px; }
.sb-hi { background: linear-gradient(90deg,#22c55e,#4ade80); }
.sb-md { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.sb-lo { background: linear-gradient(90deg,#ef4444,#f87171); }
.ch-m { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2); color: #4ade80; padding: 2px 8px; border-radius: 4px; font-size: .7rem; display: inline-block; margin: 2px; }
.ch-x { background: rgba(239,68,68,0.1);  border: 1px solid rgba(239,68,68,0.2);  color: #f87171; padding: 2px 8px; border-radius: 4px; font-size: .7rem; display: inline-block; margin: 2px; }
.summary-box { background: rgba(59,130,246,0.05); border-left: 3px solid #3b82f6; border-radius: 0 10px 10px 0; padding: 12px 16px; font-size: .84rem; color: var(--text-mid); line-height: 1.65; margin: 8px 0; }
.upload-bar { height: 3px; background: linear-gradient(90deg,#22c55e,#4ade80); border-radius: 99px; margin-top: 10px; box-shadow: 0 2px 12px rgba(34,197,94,0.4); }

/* ════════════════ ABOUT / HIW PAGES ═══════════════ */
.page-hero { text-align: center; padding: 60px 1rem 40px; }
.page-title {
    font-family: var(--font-d); font-weight: 800;
    font-size: clamp(1.8rem,4vw,3rem); line-height: 1.1; letter-spacing: -0.02em;
    color: var(--text-hi); margin-bottom: 16px; animation: fadeUp 0.7s 0.1s ease both;
}
.about-desc { color: var(--text-mid); font-size: 1.05rem; font-weight: 300; max-width: 680px; margin: 0 auto; line-height: 1.8; animation: fadeUp 0.7s 0.2s ease both; }
.div-line { height: 1px; background: linear-gradient(90deg,transparent,rgba(59,130,246,0.3),rgba(139,92,246,0.25),transparent); margin: 2rem 0; }
.feat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin: 1.5rem 0; }
.feat-card { padding: 28px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--r-xl); backdrop-filter: blur(12px); transition: var(--tr); }
.feat-card:hover { transform: translateY(-6px); border-color: var(--border-g); box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.feat-icon  { font-size: 2rem; margin-bottom: 14px; filter: drop-shadow(0 0 10px var(--primary-g)); }
.feat-title { font-family: var(--font-d); font-weight: 700; font-size: 1rem; color: var(--text-hi); margin-bottom: 8px; }
.feat-desc  { color: var(--text-mid); font-size: .85rem; line-height: 1.7; }
.impact-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin: 1.5rem 0; }
.impact-card { padding: 36px 28px; text-align: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--r-xl); transition: var(--tr); }
.impact-card:hover { transform: translateY(-4px); }
.impact-value { font-family: var(--font-d); font-weight: 800; font-size: 3.5rem; background: linear-gradient(135deg,#60a5fa,#a78bfa); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; line-height: 1; margin-bottom: 12px; }
.impact-label { color: var(--text-mid); font-size: .9rem; line-height: 1.5; }
.timeline { position: relative; max-width: 760px; margin: 0 auto; }
.timeline::before { content: ''; position: absolute; left: 32px; top: 0; bottom: 0; width: 1px; background: linear-gradient(180deg,transparent,var(--primary),var(--accent),transparent); }
.tl-item { display: flex; gap: 32px; margin-bottom: 28px; animation: fadeUp 0.6s ease both; }
.tl-item:nth-child(1){animation-delay:.1s} .tl-item:nth-child(2){animation-delay:.2s}
.tl-item:nth-child(3){animation-delay:.3s} .tl-item:nth-child(4){animation-delay:.4s}
.tl-item:nth-child(5){animation-delay:.5s} .tl-item:nth-child(6){animation-delay:.6s}
.tl-marker { flex-shrink: 0; width: 64px; height: 64px; background: linear-gradient(135deg,var(--primary),var(--accent)); border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1; box-shadow: 0 0 20px var(--primary-g); font-family: var(--font-d); font-weight: 800; font-size: .9rem; color: white; }
.tl-card { flex: 1; padding: 22px 26px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--r-xl); backdrop-filter: blur(12px); transition: var(--tr); }
.tl-card:hover { transform: translateX(6px); border-color: var(--border-g); }
.tl-ico   { font-size: 1.4rem; margin-bottom: 6px; }
.tl-title { font-family: var(--font-d); font-weight: 700; font-size: 1rem; color: var(--text-hi); margin-bottom: 6px; }
.tl-desc  { color: var(--text-mid); font-size: .87rem; line-height: 1.7; }
.tech-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(120px,1fr)); gap: 14px; }
.tech-card { padding: 22px 14px; text-align: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--r-xl); backdrop-filter: blur(12px); transition: var(--tr); }
.tech-card:hover { transform: translateY(-6px); border-color: var(--border-g); box-shadow: 0 16px 40px rgba(0,0,0,0.3); }
.tech-emoji { font-size: 2rem; margin-bottom: 8px; }
.tech-name  { font-family: var(--font-d); font-weight: 600; font-size: .8rem; color: var(--text-mid); }
.tech-built { font-size: .72rem; letter-spacing: .2em; color: var(--text-lo); font-weight: 600; text-align: center; margin: 1rem 0; }

/* ════════════════ EXPANDER / METRIC ═══════════════ */
.streamlit-expanderHeader { background: var(--bg-card) !important; color: var(--text-hi) !important; border-radius: var(--r-md) !important; border: 1px solid var(--border) !important; font-family: var(--font-d) !important; font-weight: 600 !important; }
.streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border: 1px solid var(--border) !important; border-top: none !important; }
[data-testid="metric-container"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--r-md) !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { color: var(--text-hi) !important; font-family: var(--font-d) !important; }
[data-testid="stMetricLabel"] { color: var(--text-lo) !important; }
.stProgress > div > div { background: linear-gradient(90deg,#3b82f6,#8b5cf6) !important; border-radius: 99px !important; }
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

/* ════════════════ ANIMATIONS ═══════════════ */
@keyframes pulseDot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.3)} }
@keyframes fadeUp   { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
@keyframes pageFadeIn { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
.page-anim { animation: pageFadeIn 0.5s ease both; }

/* ════════════════════════════════════════
   RESPONSIVE — Mobile & Desktop
════════════════════════════════════════ */

/* ── TABLET (max 1024px) ── */
@media (max-width: 1024px) {
    .block-container {
        padding: 70px 1.5rem 3rem !important;
    }
    .navbar {
        padding: 0 1.5rem;
    }
    .stats-row {
        grid-template-columns: repeat(3,1fr) !important;
        gap: 0.75rem !important;
    }
    .feat-grid {
        grid-template-columns: repeat(2,1fr) !important;
    }
    .impact-row {
        grid-template-columns: repeat(3,1fr) !important;
    }
    .tech-grid {
        grid-template-columns: repeat(4,1fr) !important;
    }
}

/* ── MOBILE (max 768px) ── */
@media (max-width: 768px) {
    /* Block container */
    .block-container {
        padding: 65px 0.85rem 2.5rem !important;
    }

    /* Navbar */
    .navbar {
        padding: 0 1rem;
        height: 56px;
    }
    .nav-brand-text {
        font-size: 1rem;
    }
    /* Hide desktop nav links — hamburger takes over */
    .nav-links {
        display: none !important;
    }
    /* Show hamburger button */
    .hamburger {
        display: flex !important;
    }
    .status-badge {
        padding: 4px 8px;
        font-size: 0.62rem;
    }
    .status-dot {
        width: 6px; height: 6px;
    }
    /* Mobile menu top offset matches navbar height */
    .mobile-menu {
        top: 56px;
    }

    /* Hero */
    .hero-section {
        padding: 50px 1rem 40px;
    }
    .hero-heading {
        font-size: clamp(1.6rem, 8vw, 2.2rem) !important;
    }
    .hero-sub {
        font-size: 0.92rem !important;
    }
    .hero-badge {
        font-size: 0.68rem !important;
        padding: 5px 14px !important;
    }
    .orb-1 { width: 280px; height: 280px; }
    .orb-2 { width: 220px; height: 220px; }
    .orb-3 { width: 160px; height: 160px; }

    /* Stats — stack to 1 column on mobile */
    .stats-row {
        grid-template-columns: 1fr !important;
        gap: 0.65rem !important;
    }
    .stat-card {
        padding: 18px 20px !important;
    }
    .stat-value {
        font-size: 1.6rem !important;
    }
    .stat-icon {
        font-size: 1.8rem !important;
    }

    /* Cards */
    .glass-card {
        border-radius: 16px !important;
    }
    .card-hdr {
        padding: 20px 20px 0 !important;
    }
    .card-body {
        padding: 12px 20px 20px !important;
    }

    /* About/HIW pages */
    .feat-grid {
        grid-template-columns: 1fr !important;
    }
    .impact-row {
        grid-template-columns: 1fr !important;
        gap: 0.65rem !important;
    }
    .impact-value {
        font-size: 2.5rem !important;
    }
    .page-title {
        font-size: clamp(1.6rem, 8vw, 2.2rem) !important;
    }

    /* Timeline */
    .timeline::before { display: none !important; }
    .tl-item {
        flex-direction: column !important;
        gap: 12px !important;
    }
    .tl-marker {
        width: 48px !important; height: 48px !important;
        font-size: 0.8rem !important;
    }
    .tl-card {
        padding: 16px 18px !important;
    }

    /* Tech grid */
    .tech-grid {
        grid-template-columns: repeat(3,1fr) !important;
    }
    .tech-card {
        padding: 16px 10px !important;
    }

    /* Results table — scroll on mobile */
    .rtable {
        font-size: 0.78rem !important;
        display: block !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .rtable th, .rtable td {
        padding: 10px 12px !important;
        white-space: nowrap !important;
    }

    /* Score button full width */
    .stButton > button {
        font-size: 0.82rem !important;
        padding: 11px 16px !important;
    }

    /* Illus zone */
    .illus-zone {
        padding: 24px 14px !important;
    }
    .illus-icon {
        font-size: 2rem !important;
    }
}

/* ── SMALL MOBILE (max 480px) ── */
@media (max-width: 480px) {
    .navbar {
        padding: 0 0.75rem;
        height: 52px;
    }
    .nav-brand-text {
        font-size: 0.88rem;
    }
    .nav-links {
        display: none !important;
    }
    .hamburger {
        display: flex !important;
        width: 36px; height: 36px;
    }
    /* Hide status text on very small screens */
    .status-text {
        display: none !important;
    }
    .status-badge {
        padding: 4px 6px !important;
    }
    .mobile-menu {
        top: 52px;
    }
    .block-container {
        padding: 58px 0.65rem 2rem !important;
    }
    .hero-heading {
        font-size: clamp(1.4rem, 7vw, 1.9rem) !important;
    }
    .stats-row {
        grid-template-columns: 1fr !important;
    }
    .feat-grid {
        grid-template-columns: 1fr !important;
    }
    .impact-row {
        grid-template-columns: 1fr !important;
    }
    .tech-grid {
        grid-template-columns: repeat(2,1fr) !important;
    }
    .tl-marker {
        width: 40px !important; height: 40px !important;
        font-size: 0.72rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────
def api_get(path):
    try:    return requests.get(f"{API_URL}{path}", timeout=5).json()
    except: return {}

def api_post(path, **kw):
    try:    return requests.post(f"{API_URL}{path}", timeout=60, **kw).json()
    except Exception as e: return {"error": str(e)}

def sc(s): return "#4ade80" if s>=75 else "#fbbf24" if s>=50 else "#f87171"
def sbc(s): return "sb-hi"  if s>=75 else "sb-md"   if s>=50 else "sb-lo"

def rbadge(rec):
    c = "b-green" if rec=="SHORTLIST" else "b-amber" if rec=="MAYBE" else "b-red"
    e = "✓" if rec=="SHORTLIST" else "~" if rec=="MAYBE" else "✗"
    return f'<span class="badge {c}">{e} {rec}</span>'


# ─── API ─────────────────────────────────────────────
api_data = api_get("/")
online   = bool(api_data.get("status"))
page     = st.session_state["page"]

def lc(p): return "nav-link active" if page==p else "nav-link"

ns_cls = "status-badge online" if online else "status-badge"
ns_txt = "ONLINE" if online else "OFFLINE"

# ─── NAVBAR ──────────────────────────────────────────
st.markdown(f"""
<div class="navbar">
    <a class="nav-brand" href="?nav=home" target="_self">
        <span class="nav-brand-icon">🎯</span>
        <span class="nav-brand-text">ResumeAI</span>
    </a>
    <div class="nav-links">
        <a class="{lc('home')}"  href="?nav=home"  target="_self">Home</a>
        <a class="{lc('about')}" href="?nav=about" target="_self">About</a>
        <a class="{lc('hiw')}"   href="?nav=hiw"   target="_self">How It Works</a>
    </div>
    <div style="display:flex;align-items:center;gap:0.75rem;">
        <div class="{ns_cls}">
            <span class="status-dot"></span>
            <span class="status-text">{ns_txt}</span>
        </div>
        <label class="hamburger" for="menuToggle" aria-label="Menu">
            <span></span><span></span><span></span>
        </label>
    </div>
</div>
<input type="checkbox" id="menuToggle" style="display:none;">
<div class="mobile-menu" id="mobileMenu">
    <a class="{lc('home')}"  href="?nav=home"  target="_self">🏠 Home</a>
    <a class="{lc('about')}" href="?nav=about" target="_self">📄 About</a>
    <a class="{lc('hiw')}"   href="?nav=hiw"   target="_self">⚙️ How It Works</a>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════
if page == "about":
    st.markdown("""<div class="page-anim">""", unsafe_allow_html=True)
    st.markdown("""
    <div class="page-hero">
        <div class="hero-badge">✦ About the Platform</div>
        <h1 class="page-title">Resume<br><span class="gradient-text">Screening AI</span></h1>
        <p class="about-desc">An intelligent recruitment assistant automating candidate evaluation
        using <strong style="color:#93c5fd;">LLaMA 3 via Groq API</strong> — ultra-fast inference,
        enterprise-grade accuracy, and fully explainable results.</p>
    </div>
    <div style="font-family:var(--font-d);font-size:1.15rem;font-weight:700;color:var(--text-hi);margin-bottom:1rem;">✨ Key Features</div>
    <div class="feat-grid">
        <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">OCR Support</div><div class="feat-desc">Extract text from scanned PDFs and image-based resumes with precision using advanced OCR technology.</div></div>
        <div class="feat-card"><div class="feat-icon">🧠</div><div class="feat-title">Semantic Matching</div><div class="feat-desc">Deep contextual understanding beyond keyword matching — LLaMA 3 understands intent, context, and skill equivalence.</div></div>
        <div class="feat-card"><div class="feat-icon">📊</div><div class="feat-title">Automated Scoring</div><div class="feat-desc">Every resume receives a 0–100 score with transparent breakdown across skills, experience, and education.</div></div>
        <div class="feat-card"><div class="feat-icon">⚡</div><div class="feat-title">Fast & Scalable</div><div class="feat-desc">Groq's LPU architecture delivers sub-second inference — screen hundreds of candidates in minutes.</div></div>
        <div class="feat-card"><div class="feat-icon">🗂️</div><div class="feat-title">ATS-Friendly Output</div><div class="feat-desc">Structured JSON outputs integrate seamlessly with existing Applicant Tracking Systems.</div></div>
        <div class="feat-card"><div class="feat-icon">🎯</div><div class="feat-title">Smart Ranking</div><div class="feat-desc">SHORTLIST / MAYBE / REJECT categorization with full skill match breakdown for every candidate.</div></div>
    </div>
    <div class="div-line"></div>
    <div style="font-family:var(--font-d);font-size:1.15rem;font-weight:700;color:var(--text-hi);margin-bottom:1rem;">📈 Our Impact</div>
    <div class="impact-row">
        <div class="impact-card"><div class="impact-value">80%</div><div class="impact-label">Reduction in Manual Screening Time</div></div>
        <div class="impact-card"><div class="impact-value">3×</div><div class="impact-label">Improvement in Hiring Accuracy</div></div>
        <div class="impact-card"><div class="impact-value">100%</div><div class="impact-label">Standardized Evaluation Process</div></div>
    </div>
    <div class="div-line"></div>
    <div class="tech-built">BUILT WITH</div>
    <div style="display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:10px;padding-bottom:2rem;">
        <span style="font-family:var(--font-d);font-weight:700;font-size:.85rem;color:var(--text-mid);">⚡ GROQ</span>
        <span style="color:var(--text-lo);">·</span>
        <span style="font-family:var(--font-d);font-weight:700;font-size:.85rem;color:var(--text-mid);">🦙 LLAMA 3</span>
        <span style="color:var(--text-lo);">·</span>
        <span style="font-family:var(--font-d);font-weight:700;font-size:.85rem;color:var(--text-mid);">🌐 STREAMLIT</span>
        <span style="color:var(--text-lo);">·</span>
        <span style="font-family:var(--font-d);font-weight:700;font-size:.85rem;color:var(--text-mid);">🐍 PYTHON</span>
        <span style="color:var(--text-lo);">·</span>
        <span style="font-family:var(--font-d);font-weight:700;font-size:.85rem;color:var(--text-mid);">🚀 FASTAPI</span>
    </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════
#  HOW IT WORKS
# ═══════════════════════════════════════════════════════
if page == "hiw":
    st.markdown("""<div class="page-anim">""", unsafe_allow_html=True)
    st.markdown("""
    <div class="page-hero">
        <div class="hero-badge">✦ Step-by-Step Guide</div>
        <h1 class="page-title">How It <span class="gradient-text">Works</span></h1>
        <p class="about-desc">From job description to ranked candidates in seconds — Groq LLaMA 3 does the heavy lifting.</p>
    </div>
    <div class="div-line"></div>
    <div class="timeline">
        <div class="tl-item"><div class="tl-marker">01</div><div class="tl-card"><div class="tl-ico">📋</div><div class="tl-title">Upload Job Description</div><div class="tl-desc">Define the role with title, description, required skills, experience, and education level. This forms the AI scoring benchmark.</div></div></div>
        <div class="tl-item"><div class="tl-marker">02</div><div class="tl-card"><div class="tl-ico">📂</div><div class="tl-title">Upload Resumes</div><div class="tl-desc">Upload multiple resumes in PDF, DOCX, DOC, or TXT format. The system supports bulk upload for entire candidate pools.</div></div></div>
        <div class="tl-item"><div class="tl-marker">03</div><div class="tl-card"><div class="tl-ico">🧠</div><div class="tl-title">AI Extraction via LLaMA 3</div><div class="tl-desc">LLaMA 3 parses each resume, extracting name, skills, years of experience, education, and key achievements.</div></div></div>
        <div class="tl-item"><div class="tl-marker">04</div><div class="tl-card"><div class="tl-ico">🎯</div><div class="tl-title">Semantic Matching & Scoring</div><div class="tl-desc">Each candidate is compared against the JD semantically. Matched and missing skills are identified, and a holistic 0–100 score is generated.</div></div></div>
        <div class="tl-item"><div class="tl-marker">05</div><div class="tl-card"><div class="tl-ico">📊</div><div class="tl-title">Ranking & Recommendation</div><div class="tl-desc">Candidates are ranked by score and assigned SHORTLIST (≥75), MAYBE (50–74), or REJECT (&lt;50) recommendations.</div></div></div>
        <div class="tl-item"><div class="tl-marker">06</div><div class="tl-card"><div class="tl-ico">⚡</div><div class="tl-title">Instant Results</div><div class="tl-desc">A ranked results table is displayed with scores, skill matches, and expandable detail views — ready for your hiring team immediately.</div></div></div>
    </div>
    <div class="div-line"></div>
    <div style="font-family:var(--font-d);font-size:1.15rem;font-weight:700;color:var(--text-hi);margin-bottom:1.25rem;">🛠️ Tech Stack</div>
    <div class="tech-grid">
        <div class="tech-card"><div class="tech-emoji">⚡</div><div class="tech-name">Groq API</div></div>
        <div class="tech-card"><div class="tech-emoji">🦙</div><div class="tech-name">LLaMA 3</div></div>
        <div class="tech-card"><div class="tech-emoji">🌐</div><div class="tech-name">Streamlit</div></div>
        <div class="tech-card"><div class="tech-emoji">🐍</div><div class="tech-name">Python</div></div>
        <div class="tech-card"><div class="tech-emoji">🚀</div><div class="tech-name">FastAPI</div></div>
        <div class="tech-card"><div class="tech-emoji">📄</div><div class="tech-name">PyMuPDF</div></div>
        <div class="tech-card"><div class="tech-emoji">🔍</div><div class="tech-name">OCR</div></div>
        <div class="tech-card"><div class="tech-emoji">📊</div><div class="tech-name">JSON Schema</div></div>
    </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════════
resumes_n   = api_data.get("resumes_uploaded", 0)
jd_display  = api_data.get("jd_title") or "None"
shortlisted = st.session_state.get("shortlisted", 0)
model_name  = api_data.get("model", "")

# HERO with orbs (exact HTML structure from index_fixed)
pill_cls = "api-pill on" if online else "api-pill off"
pill_dot = "ndot g" if online else "ndot y"
pill_txt = f"API Ready · {model_name}" if online else "⚠️ Backend offline — uvicorn backend:fapp --port 8000"

st.markdown(f"""
<div class="page-anim">
<div class="hero-section">
    <div class="hero-bg-grid"></div>
    <div class="hero-orb orb-1"></div>
    <div class="hero-orb orb-2"></div>
    <div class="hero-orb orb-3"></div>
    <div class="hero-content">
        <div class="hero-badge">✦ AI-Powered Recruitment Platform</div>
        <h1 class="hero-heading">Resume<br><span class="gradient-text">Screening AI</span></h1>
        <p class="hero-sub">Powered by Groq ⚡ LLaMA 3 — ultra-fast AI candidate scoring</p>
        <div style="display:flex;justify-content:center;">
            <div class="{pill_cls}">
                <span class="{pill_dot}"></span>
                {pill_txt}
            </div>
        </div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# STATS
jd_val_cls = "stat-value stat-value-sm" if len(jd_display) > 14 else "stat-value"
st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div><div class="stat-value">{resumes_n}</div><div class="stat-label">Resumes Uploaded</div></div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">💼</div>
        <div><div class="{jd_val_cls}">{jd_display}</div><div class="stat-label">Active Job</div></div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div><div class="stat-value">{shortlisted}</div><div class="stat-label">Shortlisted</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# TWO COLUMNS
left, right = st.columns(2, gap="large")

with left:
    # Decorative card header
    st.markdown("""
    <div class="glass-card">
        <div class="card-hdr">
            <div class="sec-row">
                <div class="sec-ico">📋</div>
                <div>
                    <div class="sec-title">Job Description</div>
                    <div class="sec-sub" style="color:#ffffff;opacity:0.8;">Step 1 — Define the role you are hiring for</div>
                </div>
            </div>
            <div class="card-div"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    jd_title  = st.text_input("Job Title",       placeholder="e.g. Senior Python Developer",                     key="jd_t")
    jd_desc   = st.text_area ("Description",      placeholder="Describe the role, responsibilities, and requirements...", height=115, key="jd_d")
    jd_skills = st.text_input("Required Skills",  placeholder="python, django, docker, postgresql",               key="jd_s")
    c1, c2    = st.columns(2)
    with c1:   jd_exp = st.number_input("Min Experience (yrs)", min_value=0, max_value=20, value=0, key="jd_e")
    with c2:   jd_edu = st.selectbox("Education Level", ["not specified","diploma","associate","bachelors","masters","phd"], key="jd_edu")

    if st.button("💼  Upload Job Description", type="primary", key="btn_jd"):
        if not jd_title or not jd_desc:
            st.error("⚠️ Job title and description are required!")
        else:
            with st.spinner("Uploading..."):
                res = api_post("/upload-jd", json={
                    "title": jd_title, "description": jd_desc,
                    "skills_required": [s.strip() for s in jd_skills.split(",") if s.strip()],
                    "experience_years": jd_exp if jd_exp > 0 else None,
                    "education": jd_edu
                })
            if res.get("jd_id"):
                st.success(f"✅ Uploaded: **{jd_title}**")
                st.markdown('<div class="upload-bar"></div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.error(res.get("error", "Upload failed"))

with right:
    st.markdown("""
    <div class="glass-card">
        <div class="card-hdr">
            <div class="sec-row">
                <div class="sec-ico">📂</div>
                <div>
                    <div class="sec-title">Upload Resumes</div>
                    <div class="sec-sub" style="color:#ffffff;opacity:0.8;">Step 2 — Groq AI scores instantly ⚡</div>
                </div>
            </div>
            <div class="card-div"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="illus-zone">
        <div class="illus-icon">📁</div>
        <div class="illus-title">Drag &amp; Drop resumes here</div>
        <div class="illus-sub">or click to browse files</div>
        <div class="fmt-wrap">
            <span class="fmt">PDF</span>
            <span class="fmt">DOCX</span>
            <span class="fmt">DOC</span>
            <span class="fmt">TXT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    files = st.file_uploader(
        "Upload Resumes",
        type=["pdf","docx","doc","txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="rf"
    )

    if files:
        st.caption(f"📎 {len(files)} file(s) selected")

    if st.button("📤  Upload All Resumes", type="primary", key="btn_ur"):
        if not files:
            st.warning("⚠️ Please select resume files first")
        else:
            prog = st.progress(0)
            uploaded = 0
            for i, f in enumerate(files):
                with st.spinner(f"Uploading {f.name}..."):
                    f.seek(0)
                    res = api_post("/upload-resume",
                                   files={"file": (f.name, f.read(), "application/octet-stream")})
                if res.get("resume_id"):
                    p = res.get("parsed", {})
                    st.success(f"✅ {p.get('name', f.name)}")
                    uploaded += 1
                else:
                    st.error(f"❌ {f.name}: {res.get('error','Failed')}")
                prog.progress((i+1)/len(files))
            if uploaded:
                st.markdown('<div class="upload-bar"></div>', unsafe_allow_html=True)
            st.rerun()

# SCORE + CLEAR
st.markdown("<br>", unsafe_allow_html=True)
cs, cc = st.columns([5, 1])
with cs:
    score_btn = st.button("⚡  Score & Rank with Groq LLaMA 3", type="primary", key="btn_score")
with cc:
    if st.button("🗑️ Clear", type="secondary", key="btn_clear"):
        try: requests.delete(f"{API_URL}/clear", timeout=5)
        except: pass
        st.session_state.clear()
        st.rerun()

if score_btn:
    with st.spinner("⚡ Groq LLaMA 3 ranking candidates..."):
        data = api_get("/ranked-candidates")
    if data.get("error"):    st.error(data["error"])
    elif data.get("detail"): st.warning(data["detail"])
    else:
        st.session_state["results"]     = data
        st.session_state["shortlisted"] = data.get("shortlisted", 0)
        st.rerun()

# RESULTS
if "results" in st.session_state:
    data       = st.session_state["results"]
    candidates = data.get("ranked_candidates", [])
    if not candidates:
        st.info("No candidates found.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:var(--font-d);font-size:clamp(1.4rem,2.5vw,2rem);font-weight:800;color:var(--text-hi);letter-spacing:-.02em;margin-bottom:.85rem;">
            📊 Ranked Candidates
        </div>
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.25rem;">
            <span class="badge b-blue">Total: {data.get('total_candidates',0)}</span>
            <span class="badge b-green">Shortlist: {data.get('shortlisted',0)}</span>
            <span class="badge b-amber">Maybe: {data.get('maybe',0)}</span>
            <span class="badge b-red">Reject: {data.get('rejected',0)}</span>
        </div>
        """, unsafe_allow_html=True)

        f_opt    = st.radio("Filter:", ["All","SHORTLIST","MAYBE","REJECT"], horizontal=True, key="filt")
        filtered = candidates if f_opt=="All" else [c for c in candidates if c["recommendation"]==f_opt]

        rows = ""
        for i, c in enumerate(filtered):
            s   = c.get("final_score", 0)
            col = sc(s); cls = sbc(s)
            mp  = (c.get("matched_skills") or [])[:4]
            chips = "".join(f'<span class="ch-m">{sk}</span>' for sk in mp) or "<span style='color:var(--text-lo)'>—</span>"
            top3 = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            rows += f"""<tr>
                <td><span style="font-family:var(--font-d);font-weight:700;color:var(--text-mid);">{top3}</span></td>
                <td><div class="cname">{c.get('candidate_name','Unknown')}</div><div class="cfname">{c.get('filename','')}</div></td>
                <td><div class="sb-wrap">
                    <span class="sb-val" style="color:{col};">{s}</span>
                    <div class="sb-bg"><div class="sb-fill {cls}" style="width:{s}%;"></div></div>
                </div></td>
                <td><div style="display:flex;flex-wrap:wrap;gap:3px;">{chips}</div></td>
                <td>{rbadge(c.get('recommendation',''))}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-xl);backdrop-filter:blur(12px);">
            <div style="overflow-x:auto;">
            <table class="rtable">
                <thead><tr><th>Rank</th><th>Candidate</th><th>Score</th><th>Matched Skills</th><th>Status</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:var(--font-d);font-size:1.2rem;font-weight:700;color:var(--text-hi);margin-bottom:.75rem;">🔍 Detailed Breakdown</div>', unsafe_allow_html=True)

        for c in filtered:
            rec   = c.get("recommendation","")
            emoji = "✅" if rec=="SHORTLIST" else "⚠️" if rec=="MAYBE" else "❌"
            score = c.get("final_score", 0)
            with st.expander(f"{emoji}  {c.get('candidate_name','Unknown')}  —  {score}/100  ({rec})"):
                m1, m2, m3 = st.columns(3)
                m1.metric("Final Score",  f"{score}/100")
                m2.metric("Experience",   f"{c.get('experience_years','N/A')} yrs")
                m3.metric("Education",    str(c.get("education","N/A")).title())
                if c.get("summary"):
                    st.markdown(f'<div class="summary-box">💬 {c["summary"]}</div>', unsafe_allow_html=True)
                cm, cx = st.columns(2)
                with cm:
                    st.markdown("**✅ Matched Skills**")
                    matched = c.get("matched_skills",[])
                    st.markdown(" ".join(f'<span class="ch-m">{s}</span>' for s in matched) if matched else "<span style='color:var(--text-lo)'>None</span>", unsafe_allow_html=True)
                with cx:
                    st.markdown("**❌ Missing Skills**")
                    missing = c.get("missing_skills",[])
                    st.markdown(" ".join(f'<span class="ch-x">{s}</span>' for s in missing) if missing else "<span style='color:#4ade80'>None ✓</span>", unsafe_allow_html=True)