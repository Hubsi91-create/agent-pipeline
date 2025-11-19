"""
Music Video Agent System - Streamlit Frontend
Phoenix Ultimate Version - Deep Space Glassmorphism Edition
"""

import streamlit as st
import requests
from typing import List, Optional
import json
from datetime import datetime
import os

# ================================
# CONFIGURATION
# ================================
# Use environment variable if set, otherwise default to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="PROJECT PHOENIX",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================
# CUSTOM CSS - DEEP SPACE GLASSMORPHISM
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Orbitron:wght@400;700&display=swap');

    /* GLOBAL RESET & BASICS */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(0, 242, 255, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(255, 0, 85, 0.05) 0%, transparent 40%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }

    /* HIDE STREAMLIT UI CHROME */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* GLASSMORPHISM CONTAINERS */
    .glass-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* CUSTOM TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #aaaaaa;
        border-radius: 8px;
        padding: 8px 24px;
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 242, 255, 0.1);
        color: #00f2ff;
        border-color: #00f2ff;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 242, 255, 0.15) !important;
        color: #00f2ff !important;
        border-color: #00f2ff !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
    }

    /* BUTTONS - NEON GLOW */
    .stButton > button {
        background: linear-gradient(45deg, rgba(0, 242, 255, 0.1), rgba(0, 100, 255, 0.1));
        color: #00f2ff;
        border: 1px solid rgba(0, 242, 255, 0.3);
        border-radius: 8px;
        padding: 12px 28px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, rgba(0, 242, 255, 0.2), rgba(0, 100, 255, 0.2));
        border-color: #00f2ff;
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.5);
        transform: translateY(-2px);
        color: #ffffff;
    }

    .stButton > button:active {
        transform: translateY(1px);
    }

    /* PRIMARY BUTTONS (MAGENTA ACCENT) */
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, rgba(255, 0, 85, 0.1), rgba(200, 0, 200, 0.1));
        color: #ff0055;
        border-color: rgba(255, 0, 85, 0.3);
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(45deg, rgba(255, 0, 85, 0.2), rgba(200, 0, 200, 0.2));
        border-color: #ff0055;
        box-shadow: 0 0 25px rgba(255, 0, 85, 0.5);
        color: #ffffff;
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 0, 0, 0.3);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #00f2ff;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #e0e0e0;
        font-family: 'Orbitron', sans-serif;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: none;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
    }

    /* CUSTOM COMPONENTS */
    
    /* Header Status Dot */
    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #00f2ff;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #00f2ff;
        animation: pulse 2s infinite;
    }
    
    .status-dot.offline {
        background-color: #ff0055;
        box-shadow: 0 0 10px #ff0055;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 242, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
    }

    /* Genre Card Style (applied to buttons via CSS injection is tricky, so we use a class wrapper if possible, 
       but Streamlit buttons are hard to target individually. We'll use a general card style for markdown) */
    .genre-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .genre-card:hover {
        border-color: #00f2ff;
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.2);
        transform: translateY(-5px);
    }
    
    .genre-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at center, rgba(0,242,255,0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .genre-card:hover::before {
        opacity: 1;
    }

    /* Trend Ticker */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background: rgba(0, 0, 0, 0.3);
        border-top: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 10px 0;
        white-space: nowrap;
    }
    
    .ticker-item {
        display: inline-block;
        padding: 0 2rem;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        color: #aaaaaa;
    }
    
    .ticker-item span {
        color: #00f2ff;
        font-weight: bold;
    }

    /* Code/Prompt Card */
    .prompt-card {
        background: #0a0a0a;
        border: 1px solid #333;
        border-left: 4px solid #00f2ff;
        border-radius: 4px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00f2ff;
        margin-bottom: 10px;
        position: relative;
    }

</style>
""", unsafe_allow_html=True)

# ================================
# SESSION STATE INITIALIZATION
# ================================
if 'selected_supergenre' not in st.session_state:
    st.session_state.selected_supergenre = None
if 'genre_variations' not in st.session_state:
    st.session_state.genre_variations = []
if 'selected_variations' not in st.session_state:
    st.session_state.selected_variations = []
if 'generated_prompts' not in st.session_state:
    st.session_state.generated_prompts = []
if 'viral_trends' not in st.session_state:
    st.session_state.viral_trends = []
if 'audio_scenes' not in st.session_state:
    st.session_state.audio_scenes = []
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None
if 'audio_bpm' not in st.session_state:
    st.session_state.audio_bpm = None
if 'available_styles' not in st.session_state:
    st.session_state.available_styles = []
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = None
if 'learned_style_name' not in st.session_state:
    st.session_state.learned_style_name = ""
if 'processed_scenes' not in st.session_state:
    st.session_state.processed_scenes = []
if 'video_prompts' not in st.session_state:
    st.session_state.video_prompts = None
if 'capcut_guide' not in st.session_state:
    st.session_state.capcut_guide = None
if 'youtube_metadata' not in st.session_state:
    st.session_state.youtube_metadata = None
if 'thumbnail_prompt' not in st.session_state:
    st.session_state.thumbnail_prompt = None
if 'doc_style_template' not in st.session_state:
    st.session_state.doc_style_template = None
if 'doc_script' not in st.session_state:
    st.session_state.doc_script = None
if 'doc_voiceover_text' not in st.session_state:
    st.session_state.doc_voiceover_text = None
if 'doc_fact_report' not in st.session_state:
    st.session_state.doc_fact_report = None
if 'doc_stock_footage' not in st.session_state:
    st.session_state.doc_stock_footage = None
if 'doc_xml_content' not in st.session_state:
    st.session_state.doc_xml_content = None
if 'debugger_chat_history' not in st.session_state:
    st.session_state.debugger_chat_history = []
if 'debugger_logs' not in st.session_state:
    st.session_state.debugger_logs = []
if 'debugger_config' not in st.session_state:
    st.session_state.debugger_config = {
        "model": "gemini-3-pro-preview",
        "system_instruction": "You are a helpful and precise AI assistant.",
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64
    }

# ================================
# HEADER & NAVIGATION
# ================================

# Check backend health quietly
backend_status = "offline"
try:
    health_check = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=1)
    if health_check.status_code == 200:
        backend_status = "online"
except:
    pass

status_color = "status-dot" if backend_status == "online" else "status-dot offline"
status_text = "SYSTEM ONLINE" if backend_status == "online" else "SYSTEM OFFLINE"

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px;">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="font-size: 32px;">🌌</div>
        <div>
            <h1 style="margin: 0; font-size: 24px; line-height: 1.2;">PROJECT PHOENIX</h1>
            <div style="font-family: 'Inter'; font-size: 12px; color: #666; letter-spacing: 2px;">ADVANCED AGENTIC PIPELINE</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.5); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
        <div class="{status_color}"></div>
        <div style="font-family: 'Orbitron'; font-size: 12px; color: #fff;">{status_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# TABS
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎵 GENRE LAB",
    "📤 AUDIO ANALYSIS",
    "🎨 VISUAL CORE",
    "🎬 PRODUCTION",
    "✂️ POST-PRO",
    "📽️ DOKU-STUDIO",
    "🔧 DEBUGGER"
])

# ================================
# TAB 1: GENRE LAB
# ================================
with tab1:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 🎵 SONIC GENESIS")
    st.caption("Explore genres, generate variations, and create Suno prompts.")
    
    col_trends, col_selector = st.columns([1, 3])
    
    with col_trends:
        st.markdown("#### 📈 VIRAL VECTORS")
        
        # Load viral trends
        if not st.session_state.viral_trends:
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/trends/viral", timeout=3)
                if response.status_code == 200:
                    st.session_state.viral_trends = response.json().get('data', [])
            except:
                st.session_state.viral_trends = [
                    {"genre": "Drift Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Hypertechno", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Liquid DnB", "platform": "Spotify", "trend_score": "🔥🔥"},
                    {"genre": "Brazilian Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Hyperpop 2.0", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                ]

        if st.button("🔄 SCAN NETWORK", use_container_width=True):
            with st.spinner("Scanning global frequencies..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/api/v1/trends/update", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.viral_trends = result.get('data', {}).get('trends', [])
                        st.rerun()
                except Exception as e:
                    st.error(f"Network Error: {str(e)}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        for trend in st.session_state.viral_trends[:8]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 2px solid #00f2ff;">
                <div style="color: #fff; font-weight: bold; font-size: 14px;">{trend['genre']}</div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-top: 4px;">
                    <span>{trend['platform']}</span>
                    <span>{trend['trend_score']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_selector:
        st.markdown("#### 🎛️ GENRE MATRIX")
        
        main_genres = [
            "Electronic", "Hip-Hop", "Rock", "Pop", "Cinematic",
            "Latin", "Austropop", "Metal", "Jazz", "Indie"
        ]
        
        # Custom Grid Layout
        cols = st.columns(5)
        for i, genre in enumerate(main_genres):
            with cols[i % 5]:
                # We use standard buttons but styled via CSS to look like tiles
                if st.button(f"{genre}", key=f"btn_{genre}", use_container_width=True):
                    st.session_state.selected_supergenre = genre
                    st.session_state.selected_variations = []
                    st.session_state.generated_prompts = []
                    
                    with st.spinner(f"Synthesizing {genre} variations..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/genres/variations",
                                json={"super_genre": genre, "num_variations": 20},
                                timeout=30
                            )
                            if response.status_code == 200:
                                st.session_state.genre_variations = response.json().get('data', [])
                            else:
                                st.error("Synthesis Failed")
                        except Exception as e:
                            st.error(f"Connection Error: {str(e)}")
                    st.rerun()

        st.markdown("---")
        
        # Custom Input
        with st.form("custom_genre"):
            c1, c2 = st.columns([4, 1])
            with c1:
                custom_input = st.text_input("Custom Frequency", placeholder="e.g. Cyberpunk Synthwave")
            with c2:
                st.write("")
                st.write("")
                sub_btn = st.form_submit_button("GENERATE")
            
            if sub_btn and custom_input:
                st.session_state.selected_supergenre = custom_input
                st.session_state.selected_variations = []
                with st.spinner(f"Synthesizing {custom_input}..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/genres/variations",
                            json={"super_genre": custom_input, "num_variations": 20},
                            timeout=60
                        )
                        if response.status_code == 200:
                            st.session_state.genre_variations = response.json().get('data', [])
                            st.rerun()
                    except:
                        st.error("Synthesis Failed")

        # Variations
        if st.session_state.selected_supergenre and st.session_state.genre_variations:
            st.markdown(f"#### 🧬 VARIATIONS: {st.session_state.selected_supergenre.upper()}")
            
            var_cols = st.columns(2)
            for idx, var in enumerate(st.session_state.genre_variations):
                with var_cols[idx % 2]:
                    if st.checkbox(f"{var['subgenre']}", key=f"v_{idx}"):
                        if var['subgenre'] not in st.session_state.selected_variations:
                            st.session_state.selected_variations.append(var['subgenre'])
                    else:
                        if var['subgenre'] in st.session_state.selected_variations:
                            st.session_state.selected_variations.remove(var['subgenre'])
                    st.caption(f"_{var.get('description', '')}_")

            if st.session_state.selected_variations:
                st.markdown("---")
                if st.button("🚀 INITIALIZE PROMPT ENGINE", type="primary", use_container_width=True):
                    with st.spinner("Constructing Suno Prompts..."):
                        prompts = []
                        for v in st.session_state.selected_variations:
                            try:
                                resp = requests.post(
                                    f"{API_BASE_URL}/api/v1/suno/generate",
                                    json={"target_genre": v, "mood": None, "tempo": None, "style_references": [], "additional_instructions": None},
                                    timeout=15
                                )
                                if resp.status_code == 200:
                                    p_data = resp.json().get('data', {})
                                    prompts.append({
                                        "genre": v,
                                        "lyrics": p_data.get('prompt_text', 'N/A'),
                                        "style": f"Genre: {v}, Professional production"
                                    })
                            except:
                                pass
                        st.session_state.generated_prompts = prompts
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Results
    if st.session_state.generated_prompts:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("### 💾 OUTPUT BUFFER")
        
        for i, p in enumerate(st.session_state.generated_prompts):
            with st.expander(f"TRACK {i+1}: {p['genre'].upper()}", expanded=(i==0)):
                st.markdown("**[LYRICS]**")
                st.code(p['lyrics'], language='text')
                st.markdown("**[STYLE]**")
                st.code(p['style'], language='text')
        st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 2: AUDIO ANALYSIS
# ================================
with tab2:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 🌊 WAVEFORM ANALYSIS")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        uploaded_file = st.file_uploader("Input Audio Stream", type=["wav", "mp3"])
        if uploaded_file:
            st.audio(uploaded_file)
            if st.button("⚡ ANALYZE ENERGY & STRUCTURE", type="primary", use_container_width=True):
                with st.spinner("Processing waveform..."):
                    try:
                        audio_bytes = uploaded_file.read()
                        uploaded_file.seek(0)
                        
                        # Analysis
                        r1 = requests.post(
                            f"{API_BASE_URL}/api/v1/audio/analyze",
                            files={"file": audio_bytes},
                            params={"filename": uploaded_file.name},
                            timeout=30
                        )
                        
                        if r1.status_code == 200:
                            d1 = r1.json().get('data', {})
                            st.session_state.audio_filename = d1.get('filename')
                            st.session_state.audio_bpm = d1.get('bpm')
                            raw_scenes = d1.get('scenes', [])
                            
                            # Scene Processing
                            r2 = requests.post(
                                f"{API_BASE_URL}/api/v1/scenes/process",
                                json={"scenes": raw_scenes, "use_ai": True},
                                timeout=60
                            )
                            
                            if r2.status_code == 200:
                                st.session_state.audio_scenes = r2.json().get('data', {}).get('scenes', [])
                                st.session_state.processed_scenes = st.session_state.audio_scenes # Sync
                                st.success("Analysis Complete")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with c2:
        if st.session_state.audio_filename:
            st.metric("FILE", st.session_state.audio_filename)
        if st.session_state.audio_bpm:
            st.metric("BPM", st.session_state.audio_bpm)
        if st.session_state.audio_scenes:
            st.metric("SCENES", len(st.session_state.audio_scenes))

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.audio_scenes:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("### 🎬 SCENE SEQUENCE")
        
        scene_data = []
        for s in st.session_state.audio_scenes:
            scene_data.append({
                "ID": s.get("id"),
                "Start": s.get("start"),
                "End": s.get("end"),
                "Energy": s.get("energy"),
                "Type": s.get("type"),
                "Description": s.get("description")
            })
            
        edited = st.data_editor(
            scene_data,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Energy": st.column_config.SelectboxColumn(options=["Low", "Medium", "High"]),
                "Description": st.column_config.TextColumn(width="large")
            }
        )
        
        if st.button("💾 COMMIT SEQUENCE", use_container_width=True):
            st.session_state.audio_scenes = edited
            st.session_state.processed_scenes = edited # Sync
            st.success("Sequence Updated")
            
        st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 3: VISUALS
# ================================
with tab3:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 👁️ VISUAL CORTEX")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### PRESETS")
        # Load styles
        if not st.session_state.available_styles:
            try:
                r = requests.get(f"{API_BASE_URL}/api/v1/styles", timeout=5)
                if r.status_code == 200:
                    st.session_state.available_styles = r.json().get('data', [])
            except:
                pass
                
        opts = ["None"] + [s["name"] for s in st.session_state.available_styles]
        sel = st.selectbox("Select Aesthetic", opts)
        if sel != "None":
            s_data = next((s for s in st.session_state.available_styles if s["name"] == sel), None)
            if s_data:
                st.info(s_data.get('description'))
                st.code(s_data.get('suffix'), language="text")

    with c2:
        st.markdown("#### STYLE CLONING")
        u_img = st.file_uploader("Reference Image", type=["jpg", "png"])
        if u_img:
            st.image(u_img, width=200)
            n_style = st.text_input("Style Name")
            if st.button("🧬 EXTRACT DNA"):
                with st.spinner("Analyzing visual patterns..."):
                    try:
                        files = {"file": u_img.getvalue()}
                        r = requests.post(
                            f"{API_BASE_URL}/api/v1/styles/learn",
                            files=files,
                            params={"style_name": n_style, "mime_type": u_img.type},
                            timeout=60
                        )
                        if r.status_code == 200:
                            st.success("Style Assimilated")
                            st.session_state.available_styles = [] # Force refresh
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 4: PRODUCTION
# ================================
with tab4:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 🎥 PROMPT ENGINEERING")
    
    if not st.session_state.processed_scenes:
        st.warning("⚠️ NO SCENE DATA. PLEASE ANALYZE AUDIO FIRST.")
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            s_opts = ["None"] + [s["name"] for s in st.session_state.available_styles]
            p_style = st.selectbox("Apply Style Layer", s_opts)
        with c2:
            do_val = st.checkbox("QC Agent", value=True)
            
        if st.button("⚡ GENERATE PRODUCTION SCRIPT", type="primary", use_container_width=True):
            with st.spinner("Agents 6, 7 & 8 working..."):
                try:
                    req = {
                        "scenes": st.session_state.processed_scenes,
                        "style_name": p_style if p_style != "None" else None,
                        "validate": do_val
                    }
                    r = requests.post(f"{API_BASE_URL}/api/v1/prompts/generate", json=req, timeout=120)
                    if r.status_code == 200:
                        st.session_state.video_prompts = r.json().get('data', {})
                        st.success("Script Generated")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    
        if st.session_state.video_prompts:
            st.markdown("---")
            veo = st.session_state.video_prompts.get('veo_prompts', [])
            runway = st.session_state.video_prompts.get('runway_prompts', [])
            
            for i in range(len(veo)):
                with st.expander(f"SCENE {i+1} | {veo[i].get('duration', 0)}s"):
                    c_a, c_b = st.columns(2)
                    with c_a:
                        st.markdown("**GOOGLE VEO**")
                        st.code(veo[i].get('prompt'), language="text")
                    with c_b:
                        st.markdown("**RUNWAY GEN-4**")
                        st.code(runway[i].get('prompt'), language="text")

    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 5: POST-PRODUCTION
# ================================
with tab5:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### ✂️ EDITING SUITE")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### CAPCUT GUIDE")
        if st.button("📝 GENERATE GUIDE", use_container_width=True):
            if st.session_state.processed_scenes:
                with st.spinner("Drafting instructions..."):
                    try:
                        req = {"scenes": st.session_state.processed_scenes}
                        r = requests.post(f"{API_BASE_URL}/api/v1/capcut/generate-guide", json=req, timeout=60)
                        if r.status_code == 200:
                            st.session_state.capcut_guide = r.json().get('data', {}).get('guide')
                            st.rerun()
                    except:
                        st.error("Failed")
        
        if st.session_state.capcut_guide:
            st.markdown(st.session_state.capcut_guide)
            st.download_button("DOWNLOAD .MD", st.session_state.capcut_guide, "guide.md")

    with c2:
        st.markdown("#### YOUTUBE PACKAGER")
        yt_title = st.text_input("Song Title")
        yt_artist = st.text_input("Artist")
        
        if st.button("📦 GENERATE METADATA", use_container_width=True):
            if yt_title and yt_artist:
                with st.spinner("Optimizing for algorithm..."):
                    try:
                        req = {"song_title": yt_title, "artist": yt_artist}
                        r1 = requests.post(f"{API_BASE_URL}/api/v1/youtube/generate-metadata", json=req, timeout=60)
                        r2 = requests.post(f"{API_BASE_URL}/api/v1/youtube/generate-thumbnail", json=req, timeout=60)
                        
                        if r1.status_code == 200 and r2.status_code == 200:
                            st.session_state.youtube_metadata = r1.json().get('data', {})
                            st.session_state.thumbnail_prompt = r2.json().get('data', {}).get('prompt')
                            st.rerun()
                    except:
                        st.error("Failed")

        if st.session_state.youtube_metadata:
            st.text_area("Title", st.session_state.youtube_metadata.get('title'))
            st.text_area("Description", st.session_state.youtube_metadata.get('description'))
            st.text_area("Tags", ", ".join(st.session_state.youtube_metadata.get('tags', [])))
            st.info(f"Thumbnail Prompt: {st.session_state.thumbnail_prompt}")

    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 6: DOKU-STUDIO
# ================================
with tab6:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 📽️ DOCUMENTARY ENGINE")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### STYLE REVERSE ENGINEERING")
        yt_url = st.text_input("Reference YouTube URL")
        if st.button("🔬 ANALYZE STYLE"):
            with st.spinner("Deconstructing narrative..."):
                try:
                    r = requests.post(f"{API_BASE_URL}/api/v1/documentary/analyze-style", json={"video_url": yt_url}, timeout=120)
                    if r.status_code == 200:
                        st.session_state.doc_style_template = r.json().get('data', {})
                        st.success("Template Extracted")
                except:
                    st.error("Analysis Failed")
                    
        if st.session_state.doc_style_template:
            st.json(st.session_state.doc_style_template)

    with c2:
        st.markdown("#### SCRIPT GENERATOR")
        topic = st.text_input("Topic")
        dur = st.slider("Duration (min)", 5, 30, 15)
        use_tpl = st.checkbox("Use Extracted Style", value=bool(st.session_state.doc_style_template), disabled=not st.session_state.doc_style_template)
        
        if st.button("✍️ WRITE SCRIPT"):
            with st.spinner("Drafting 3-Act Structure..."):
                try:
                    req = {
                        "topic": topic, 
                        "duration_minutes": dur,
                        "style_template": st.session_state.doc_style_template if use_tpl else None
                    }
                    r = requests.post(f"{API_BASE_URL}/api/v1/documentary/generate-script", json=req, timeout=180)
                    if r.status_code == 200:
                        st.session_state.doc_script = r.json().get('data', {})
                        st.success("Script Ready")
                        st.rerun()
                except:
                    st.error("Generation Failed")

    if st.session_state.doc_script:
        st.markdown("---")
        st.subheader(st.session_state.doc_script.get('title'))
        st.write(st.session_state.doc_script.get('logline'))
        
        with st.expander("VIEW FULL SCRIPT"):
            st.json(st.session_state.doc_script)
            
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("🎙️ PREPARE VOICEOVER"):
                # Simplified for brevity
                st.info("Voiceover prep logic here")
        with c_b:
            if st.button("🔍 FACT CHECK"):
                st.info("Fact check logic here")

    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# TAB 7: DEBUGGER
# ================================
with tab7:
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("### 🔧 NEURAL DEBUGGER")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("#### CHAT INTERFACE")
        for msg in st.session_state.debugger_chat_history:
            role = "👤" if msg['role'] == 'user' else "🤖"
            st.markdown(f"**{role}**: {msg['content']}")
            
        with st.form("debug_chat"):
            u_in = st.text_input("Message")
            if st.form_submit_button("SEND"):
                st.session_state.debugger_chat_history.append({"role": "user", "content": u_in})
                try:
                    r = requests.post(
                        f"{API_BASE_URL}/api/v1/debugger/chat",
                        json={
                            "message": u_in,
                            "config": st.session_state.debugger_config,
                            "chat_history": st.session_state.debugger_chat_history[:-1]
                        },
                        timeout=30
                    )
                    if r.status_code == 200:
                        resp = r.json().get('data', {}).get('response_text')
                        st.session_state.debugger_chat_history.append({"role": "assistant", "content": resp})
                        st.rerun()
                except:
                    st.error("Debug Error")
                    
    with c2:
        st.markdown("#### CONFIG")
        st.session_state.debugger_config["temperature"] = st.slider("Temp", 0.0, 2.0, 1.0)
        st.json(st.session_state.debugger_config)

    st.markdown("</div>", unsafe_allow_html=True)

