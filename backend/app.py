"""
Music Video Agent System - Streamlit Frontend
Phoenix Ultimate Version
"""

import streamlit as st
import requests
from typing import List, Optional
import json

# ================================
# CONFIGURATION
# ================================
# Hardcoded internal loopback address for Cloud Run (same container)
# FastAPI and Streamlit run in the same container, communicate via 127.0.0.1
# NOTE: No /api/v1 suffix here - the frontend adds it to each endpoint
API_BASE_URL = "http://127.0.0.1:8000"

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="Music Video Agent System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CUSTOM CSS - DARK MODE
# ================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f0f1e;
        color: #e0e0e0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #16213e;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border-radius: 4px;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0f4c75;
        color: #ffffff;
    }

    /* Buttons */
    .stButton > button {
        background-color: #3282b8;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #0f4c75;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border: 1px solid #3282b8;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1a1a2e;
        border: 2px dashed #3282b8;
        border-radius: 4px;
        padding: 20px;
    }

    /* Headers */
    h1, h2, h3 {
        color: #3282b8;
    }

    /* Success/Error messages */
    .stSuccess {
        background-color: #1a4d2e;
    }

    .stError {
        background-color: #4d1a1a;
    }

    /* Checkboxes and radio */
    [data-testid="stCheckbox"] label {
        color: #e0e0e0;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a2e;
        color: #3282b8;
    }

    /* Genre Button Tiles (Netflix-style) */
    .genre-button {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #3282b8;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .genre-button:hover {
        background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%);
        transform: translateY(-4px);
        box-shadow: 0 8px 12px rgba(50, 130, 184, 0.4);
        border-color: #5ca0d3;
    }

    .genre-button.selected {
        background: linear-gradient(135deg, #3282b8 0%, #0f4c75 100%);
        border-color: #5ca0d3;
        box-shadow: 0 8px 16px rgba(50, 130, 184, 0.6);
    }

    /* Trend Ticker */
    .trend-item {
        background-color: #1a1a2e;
        border-left: 4px solid #3282b8;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }

    .trend-item:hover {
        background-color: #16213e;
        border-left-color: #5ca0d3;
        transform: translateX(4px);
    }

    /* Variation Selection */
    .variation-card {
        background-color: #1a1a2e;
        border: 1px solid #3282b8;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }

    .variation-card:hover {
        border-color: #5ca0d3;
        background-color: #16213e;
    }

    .variation-card.selected {
        border: 2px solid #5ca0d3;
        background-color: #0f4c75;
    }

    /* Prompt Display Box */
    .prompt-box {
        background-color: #0f0f1e;
        border: 2px solid #3282b8;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Monaco', 'Courier New', monospace;
        color: #e0e0e0;
        margin-bottom: 16px;
    }

    .prompt-section {
        margin-bottom: 12px;
    }

    .prompt-label {
        color: #3282b8;
        font-weight: bold;
        margin-bottom: 4px;
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

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.title("🎬 Music Video Agent")
    st.markdown("### Phoenix Ultimate Version")
    st.markdown("---")

    st.markdown("#### System Status")

    # Check backend health
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Online")
            st.json(response.json())
        else:
            st.error("⚠️ Backend Issues")
    except Exception as e:
        st.error("❌ Backend Offline")
        st.caption(f"Error: {str(e)}")

    st.markdown("---")
    st.markdown("#### Quick Stats")
    st.metric("Projects", "0", delta="0")
    st.metric("Generated Videos", "0", delta="0")
    st.metric("Success Rate", "0%")

    st.markdown("---")
    st.markdown("#### Documentation")
    st.markdown("📖 [Few-Shot Learning](FEW_SHOT_LEARNING.md)")
    st.markdown("🚀 [Deployment Guide](DEPLOYMENT.md)")

# ================================
# MAIN CONTENT
# ================================
st.title("🎬 Music Video Production Pipeline")
st.markdown("**AI-Powered Music Video Generation System**")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎵 Music Generation",
    "📤 Audio Upload",
    "🎨 Visuals & Style",
    "🎬 Production",
    "✂️ Post-Production",
    "📽️ Doku-Studio"
])

# ================================
# TAB 1: MUSIC GENERATION (NETFLIX-STYLE)
# ================================
with tab1:
    st.header("🎵 Music Generation - Genre Explorer")
    st.markdown("**Select a genre, explore variations, and generate Suno prompts**")
    st.markdown("---")

    # Main layout: Trend Ticker (left) + Genre Selector (right)
    trend_col, main_col = st.columns([1, 3])

    # ================================
    # LEFT: LIVE TREND TICKER
    # ================================
    with trend_col:
        st.subheader("📊 Live Trend Ticker")
        st.caption("Top 20 Viral Genres (YouTube/TikTok/Spotify)")

        # Load viral trends (cached)
        if not st.session_state.viral_trends:
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/trends/viral", timeout=3)
                if response.status_code == 200:
                    st.session_state.viral_trends = response.json().get('data', [])
            except:
                # Fallback mock data
                st.session_state.viral_trends = [
                    {"genre": "Drift Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Hypertechno", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Liquid DnB", "platform": "Spotify", "trend_score": "🔥🔥"},
                    {"genre": "Brazilian Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Hyperpop 2.0", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
                    {"genre": "Afrobeats Fusion", "platform": "Spotify", "trend_score": "🔥🔥🔥"},
                    {"genre": "UK Drill", "platform": "YouTube", "trend_score": "🔥🔥"},
                    {"genre": "Melodic Dubstep", "platform": "YouTube", "trend_score": "🔥🔥"},
                    {"genre": "Lofi House", "platform": "YouTube", "trend_score": "🔥🔥"},
                    {"genre": "Emo Rap Revival", "platform": "TikTok", "trend_score": "🔥🔥"},
                ]

        # Update button
        if st.button("🔄 Update Trends from Web", use_container_width=True, key="update_trends_btn"):
            with st.spinner("Agent 1 searching TikTok, Spotify, and YouTube Shorts with Google Search..."):
                try:
                    # Increased timeout for Google Search Grounding (can take 30-60 seconds)
                    response = requests.post(f"{API_BASE_URL}/api/v1/trends/update", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.viral_trends = result.get('data', {}).get('trends', [])
                        st.success(f"✅ Database updated! {result.get('data', {}).get('count', 0)} trends loaded")
                        st.rerun()
                    else:
                        st.error("⚠️ Failed to update trends")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

        # Display trends
        for idx, trend in enumerate(st.session_state.viral_trends[:20], 1):
            st.markdown(f"""
            <div class="trend-item">
                <strong>#{idx}</strong> {trend['genre']}<br/>
                <small style="color: #888;">{trend['platform']}</small> {trend['trend_score']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Updated: Real-time | Auto-refresh every 5 min")

    # ================================
    # RIGHT: GENRE SELECTOR + WORKFLOW
    # ================================
    with main_col:
        # Genre Button Grid
        st.subheader("🎭 Select Super Genre")

        # Define main genres
        main_genres = [
            "Electronic", "Hip-Hop", "Rock", "Pop", "Cinematic",
            "Latin", "Austropop", "Metal", "Jazz", "Indie"
        ]

        # Create button grid (5 columns x 2 rows)
        cols_per_row = 5
        for row in range(0, len(main_genres), cols_per_row):
            cols = st.columns(cols_per_row)
            for idx, col in enumerate(cols):
                genre_idx = row + idx
                if genre_idx < len(main_genres):
                    genre = main_genres[genre_idx]
                    with col:
                        # Visual highlight if selected
                        button_type = "primary" if st.session_state.selected_supergenre == genre else "secondary"

                        if st.button(
                            f"🎵 {genre}",
                            key=f"genre_btn_{genre}",
                            use_container_width=True,
                            type=button_type
                        ):
                            st.session_state.selected_supergenre = genre
                            st.session_state.selected_variations = []
                            st.session_state.generated_prompts = []

                            # Trigger variation generation
                            with st.spinner(f"Generating 20 {genre} variations with AI..."):
                                try:
                                    response = requests.post(
                                        f"{API_BASE_URL}/api/v1/genres/variations",
                                        json={"super_genre": genre, "num_variations": 20},
                                        timeout=30  # Increased for complex AI generation
                                    )
                                    if response.status_code == 200:
                                        st.session_state.genre_variations = response.json().get('data', [])
                                    else:
                                        # Show error message to user
                                        st.error(f"⚠️ API Error ({response.status_code}): {response.text[:200]}")
                                        # Fallback mock
                                        st.session_state.genre_variations = [
                                            {"subgenre": f"{genre} Style {i+1}", "description": f"Variation {i+1}"}
                                            for i in range(20)
                                        ]
                                except Exception as e:
                                    # Show exception details to user
                                    st.error(f"❌ Request failed: {str(e)}")
                                    # Fallback mock
                                    st.session_state.genre_variations = [
                                        {"subgenre": f"{genre} Style {i+1}", "description": f"Variation {i+1}"}
                                        for i in range(20)
                                    ]

                            st.rerun()

        # Custom Genre Input (Fix: Stables Formular)
        st.markdown("---")
        st.subheader("➕ Custom Genre")

        with st.form(key="custom_genre_form"):
            col_input, col_btn = st.columns([3, 1])
            with col_input:
                custom_genre_input = st.text_input("Genre eingeben", placeholder="z.B. Space Jazz")
            with col_btn:
                st.write("") # Spacer
                st.write("")
                submit_button = st.form_submit_button(label="🚀 Generate", use_container_width=True)

            if submit_button and custom_genre_input:
                st.session_state.selected_supergenre = custom_genre_input
                # Reset previous results
                st.session_state.selected_variations = []
                st.session_state.generated_prompts = []

                # Trigger generation
                with st.spinner(f"Agent 1 generiert Variationen für '{custom_genre_input}'..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/genres/variations",
                            json={"super_genre": custom_genre_input, "num_variations": 20},
                            timeout=60
                        )

                        if response.status_code == 200:
                            data = response.json().get('data', [])
                            st.session_state.genre_variations = data
                            st.success(f"✅ 20 Variationen für {custom_genre_input} gefunden!")
                            st.rerun()
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Verbindungsfehler: {str(e)}")

        # ================================
        # VARIATIONS SELECTION (appears after genre selection)
        # ================================
        if st.session_state.selected_supergenre and st.session_state.genre_variations:
            st.markdown("---")
            st.subheader(f"🎯 {st.session_state.selected_supergenre} Variations")
            st.caption(f"Select subgenres to generate Suno prompts (max 10)")

            # Display variations as checkboxes
            variation_cols = st.columns(2)

            for idx, variation in enumerate(st.session_state.genre_variations):
                col_idx = idx % 2
                with variation_cols[col_idx]:
                    checkbox_key = f"var_check_{idx}"
                    is_selected = st.checkbox(
                        f"**{variation['subgenre']}**",
                        key=checkbox_key,
                        value=variation['subgenre'] in st.session_state.selected_variations
                    )

                    if is_selected and variation['subgenre'] not in st.session_state.selected_variations:
                        if len(st.session_state.selected_variations) < 10:
                            st.session_state.selected_variations.append(variation['subgenre'])
                    elif not is_selected and variation['subgenre'] in st.session_state.selected_variations:
                        st.session_state.selected_variations.remove(variation['subgenre'])

                    st.caption(f"_{variation.get('description', 'No description')}_")

            # Generate Prompts Button
            st.markdown("---")
            if st.session_state.selected_variations:
                st.info(f"✅ {len(st.session_state.selected_variations)} variation(s) selected")

                if st.button(
                    f"🚀 Generate Suno Prompts ({len(st.session_state.selected_variations)} variations)",
                    type="primary",
                    use_container_width=True
                ):
                    with st.spinner("Generating Suno prompts..."):
                        prompts = []
                        for variation in st.session_state.selected_variations:
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/api/v1/suno/generate",
                                    json={
                                        "target_genre": variation,
                                        "mood": None,
                                        "tempo": None,
                                        "style_references": [],
                                        "additional_instructions": None
                                    },
                                    timeout=15
                                )
                                if response.status_code == 200:
                                    prompt_data = response.json().get('data', {})
                                    prompts.append({
                                        "genre": variation,
                                        "lyrics": prompt_data.get('prompt_text', 'N/A'),
                                        "style": f"Genre: {variation}, Professional production"
                                    })
                            except:
                                # Fallback mock
                                prompts.append({
                                    "genre": variation,
                                    "lyrics": f"[Verse 1]\nEpic {variation} track\nWith dynamic energy\n\n[Chorus]\nProfessional quality\nCinematic sound",
                                    "style": f"Genre: {variation}, Modern production, High energy"
                                })

                        st.session_state.generated_prompts = prompts
                        st.success(f"✅ Generated {len(prompts)} Suno prompts!")

        # ================================
        # PROMPT DISPLAY (appears after generation)
        # ================================
        if st.session_state.generated_prompts:
            st.markdown("---")
            st.subheader("📋 Generated Suno Prompts")
            st.caption("Copy and paste into Suno AI")

            for idx, prompt in enumerate(st.session_state.generated_prompts, 1):
                with st.expander(f"🎵 Prompt {idx}: {prompt['genre']}", expanded=idx==1):
                    st.markdown("**[LYRICS]**")
                    st.markdown("*Click the copy icon in the top-right corner to copy to clipboard*")
                    st.code(
                        prompt['lyrics'],
                        language='text'
                    )

                    st.markdown("**[STYLE]**")
                    st.code(
                        prompt['style'],
                        language='text'
                    )

            # Export all button
            st.markdown("---")
            if st.button("💾 Export All Prompts (JSON)", use_container_width=True):
                import json as json_module
                export_data = json_module.dumps(st.session_state.generated_prompts, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=export_data,
                    file_name="suno_prompts_export.json",
                    mime="application/json"
                )

# ================================
# TAB 2: AUDIO ANALYSIS & SCENE PLANNING
# ================================
# Session state for audio analysis
if 'audio_scenes' not in st.session_state:
    st.session_state.audio_scenes = []
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None
if 'audio_bpm' not in st.session_state:
    st.session_state.audio_bpm = None

with tab2:
    st.header("📤 Audio Analysis & Scene Planning")
    st.markdown("**Upload audio, analyze energy, and create cut-ready scene plan**")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Step 1: Upload Audio")

        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=["wav", "mp3"],
            accept_multiple_files=False,
            help="Unterstützte Formate: WAV, MP3"
        )

        if uploaded_file:
            st.success(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

            # Audio player
            st.audio(uploaded_file)

            # Analyze & Plan button
            st.markdown("---")
            if st.button("🎬 Analyze & Plan Scenes", type="primary", use_container_width=True):
                with st.spinner("Agent 3 analyzing audio energy... Agent 4 planning scenes..."):
                    try:
                        # Step 1: Analyze audio with Agent 3
                        audio_bytes = uploaded_file.read()
                        uploaded_file.seek(0)  # Reset for audio player

                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/audio/analyze",
                            files={"file": audio_bytes},
                            params={"filename": uploaded_file.name},
                            timeout=30
                        )

                        if response.status_code == 200:
                            analysis_data = response.json().get('data', {})
                            scenes = analysis_data.get('scenes', [])
                            st.session_state.audio_filename = analysis_data.get('filename')
                            st.session_state.audio_bpm = analysis_data.get('bpm')

                            # Step 2: Process scenes with Agent 4
                            response2 = requests.post(
                                f"{API_BASE_URL}/api/v1/scenes/process",
                                json={
                                    "scenes": scenes,
                                    "use_ai": True
                                },
                                timeout=60
                            )

                            if response2.status_code == 200:
                                enhanced_scenes = response2.json().get('data', {}).get('scenes', [])
                                st.session_state.audio_scenes = enhanced_scenes

                                st.success(f"✅ Analysis complete! {len(enhanced_scenes)} scenes created")
                                st.balloons()
                            else:
                                st.error("⚠️ Scene processing failed")
                        else:
                            st.error("⚠️ Audio analysis failed")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with col2:
        st.subheader("Quick Info")

        if st.session_state.audio_filename:
            st.info(f"**File:** {st.session_state.audio_filename}")

        if st.session_state.audio_bpm:
            st.metric("BPM", st.session_state.audio_bpm)

        if st.session_state.audio_scenes:
            st.metric("Scenes", len(st.session_state.audio_scenes))

        st.markdown("---")
        st.markdown("**Technical Limits:**")
        st.caption("🎥 Veo/Runway: Max 8s per scene")
        st.caption("🔄 Auto-split: Long sections")
        st.caption("⚡ Energy: Low/Medium/High")

    # Interactive Scene Table
    if st.session_state.audio_scenes:
        st.markdown("---")
        st.subheader("Step 2: Edit Scene Plan")
        st.caption("Edit timings, camera, lighting, or descriptions directly in the table")

        # Prepare data for st.data_editor
        scene_data = []
        for scene in st.session_state.audio_scenes:
            scene_data.append({
                "Scene #": scene.get("id", 0),
                "Start (s)": scene.get("start", 0.0),
                "End (s)": scene.get("end", 0.0),
                "Duration (s)": scene.get("duration", 0.0),
                "Type": scene.get("type", ""),
                "Energy": scene.get("energy", ""),
                "Camera": scene.get("camera", ""),
                "Lighting": scene.get("lighting", ""),
                "Description": scene.get("description", "")
            })

        # Interactive editable table
        edited_data = st.data_editor(
            scene_data,
            use_container_width=True,
            num_rows="dynamic",  # Allow adding/deleting rows
            column_config={
                "Scene #": st.column_config.NumberColumn("Scene #", disabled=True),
                "Start (s)": st.column_config.NumberColumn("Start (s)", format="%.2f"),
                "End (s)": st.column_config.NumberColumn("End (s)", format="%.2f"),
                "Duration (s)": st.column_config.NumberColumn("Duration (s)", format="%.2f", disabled=True),
                "Type": st.column_config.TextColumn("Type"),
                "Energy": st.column_config.SelectboxColumn("Energy", options=["Low", "Medium", "High"]),
                "Camera": st.column_config.TextColumn("Camera"),
                "Lighting": st.column_config.TextColumn("Lighting"),
                "Description": st.column_config.TextColumn("Description", width="large")
            },
            hide_index=True,
            key="scene_editor"
        )

        # Save button
        st.markdown("---")
        col_save1, col_save2, col_save3 = st.columns([1, 1, 1])

        with col_save1:
            if st.button("💾 Save Scene Plan", use_container_width=True):
                st.session_state.audio_scenes = edited_data
                st.success("✅ Scene plan saved!")

        with col_save2:
            if st.button("📥 Export as JSON", use_container_width=True):
                import json as json_module
                export_data = json_module.dumps(edited_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=export_data,
                    file_name="scene_plan.json",
                    mime="application/json"
                )

        with col_save3:
            if st.button("📄 Export as CSV", use_container_width=True):
                import pandas as pd
                df = pd.DataFrame(edited_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="scene_plan.csv",
                    mime="text/csv"
                )

# ================================
# TAB 3: VISUALS & STYLE
# ================================
# Session state for styles
if 'available_styles' not in st.session_state:
    st.session_state.available_styles = []
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = None
if 'learned_style_name' not in st.session_state:
    st.session_state.learned_style_name = ""

with tab3:
    st.header("🎨 Visuals & Style Management")
    st.markdown("**Choose a global look or teach the AI a new style from your reference images**")
    st.markdown("---")

    # Top section: Style Selector (left) + Style Learning (right)
    style_col1, style_col2 = st.columns([1, 1])

    # ================================
    # LEFT: STYLE PRESETS
    # ================================
    with style_col1:
        st.subheader("📚 Choose Global Look")

        # Load available styles
        if not st.session_state.available_styles:
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/styles", timeout=5)
                if response.status_code == 200:
                    st.session_state.available_styles = response.json().get('data', [])
            except:
                # Fallback
                st.session_state.available_styles = [
                    {"name": "CineStill 800T", "description": "Tungsten-balanced film with neon glow"},
                    {"name": "Blade Runner 2049", "description": "Neo-noir sci-fi aesthetic"}
                ]

        # Dropdown for style selection
        style_options = ["None"] + [style["name"] for style in st.session_state.available_styles]
        selected_style_name = st.selectbox(
            "Select a visual style preset",
            options=style_options,
            key="style_selector"
        )

        if selected_style_name != "None":
            # Find selected style details
            selected_style_data = next(
                (s for s in st.session_state.available_styles if s["name"] == selected_style_name),
                None
            )

            if selected_style_data:
                st.session_state.selected_style = selected_style_data

                # Display style details
                st.markdown("---")
                st.markdown("**📋 Style Details:**")
                st.info(f"**{selected_style_data['name']}**\n\n{selected_style_data.get('description', 'No description')}")

                if selected_style_data.get('suffix'):
                    st.markdown("**🎬 Prompt Suffix:**")
                    st.code(selected_style_data['suffix'], language=None)

                if selected_style_data.get('negative'):
                    st.markdown("**🚫 Negative Prompt:**")
                    st.caption(selected_style_data['negative'])

    # ================================
    # RIGHT: STYLE LEARNING
    # ================================
    with style_col2:
        st.subheader("🧠 Learn New Style")

        with st.expander("📖 How Style Learning Works", expanded=False):
            st.markdown("""
            **AI-Powered Style Cloning:**
            1. Upload a reference image with your desired aesthetic
            2. Gemini Vision analyzes lighting, color grading, and composition
            3. AI generates a compact "prompt suffix" describing the style
            4. Style is saved permanently to your database

            **What gets analyzed:**
            - Lighting (hard/soft, direction, color temperature)
            - Color grading (tones, contrast, saturation)
            - Film stock aesthetic (grain, texture)
            - Depth of field and bokeh
            - Overall mood and composition
            """)

        st.markdown("---")

        # File uploader for style learning
        style_image = st.file_uploader(
            "Upload reference image for style analysis",
            type=["jpg", "jpeg", "png"],
            key="style_learning_uploader",
            help="Upload an image that represents the visual style you want to clone"
        )

        if style_image:
            st.image(style_image, caption="Reference Image", use_container_width=True)

            # Input for style name
            new_style_name = st.text_input(
                "Name for this style",
                value=st.session_state.learned_style_name,
                placeholder="e.g., 'Vintage Polaroid', 'Cyberpunk Neon', 'Film Noir'",
                key="style_name_input"
            )

            st.markdown("---")

            # Analyze & Save button
            if st.button("🔬 Analyze & Save Style", type="primary", use_container_width=True):
                if not new_style_name:
                    st.error("⚠️ Please enter a name for the style")
                else:
                    with st.spinner(f"Agent 5 analyzing '{new_style_name}' with Gemini Vision..."):
                        try:
                            # Read image bytes
                            image_bytes = style_image.read()
                            style_image.seek(0)  # Reset for preview

                            # Determine MIME type
                            mime_type = "image/jpeg"
                            if style_image.name.endswith(".png"):
                                mime_type = "image/png"

                            # Call API
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/styles/learn",
                                files={"file": image_bytes},
                                params={
                                    "style_name": new_style_name,
                                    "mime_type": mime_type
                                },
                                timeout=60
                            )

                            if response.status_code == 200:
                                result = response.json().get('data', {})
                                st.success(f"✅ {result.get('message', 'Style learned successfully!')}")

                                # Display learned style
                                if result.get('suffix'):
                                    st.markdown("**🎬 Generated Prompt Suffix:**")
                                    st.code(result['suffix'], language=None)

                                # Clear cache
                                st.session_state.available_styles = []
                                st.balloons()
                            else:
                                st.error("⚠️ Style learning failed")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

    # ================================
    # MIDDLE: AI STYLE GENERATOR (IMAGEN 4)
    # ================================
    st.markdown("---")
    st.subheader("🎨 AI Style Generator (Imagen 4)")
    st.markdown("**Describe your desired visual style, and AI will generate a reference image**")

    # Session state for generated style
    if 'generated_style_image' not in st.session_state:
        st.session_state.generated_style_image = None
    if 'generated_style_suffix' not in st.session_state:
        st.session_state.generated_style_suffix = None

    imagen_col1, imagen_col2 = st.columns([1, 1])

    with imagen_col1:
        st.markdown("**Text-to-Image Style Generation:**")

        # Text input for style description
        style_prompt = st.text_area(
            "Describe your desired look",
            value="",
            placeholder="e.g., 'Cyberpunk city at night, neon lights, rain-soaked streets, cinematic film noir aesthetic'\n\nor 'Vintage 1970s Polaroid, warm tones, soft focus, nostalgic summer vibes'",
            height=120,
            key="imagen_style_prompt"
        )

        # Aspect ratio selector
        aspect_ratio_options = {
            "1:1 Square": "1:1",
            "16:9 Widescreen": "16:9",
            "9:16 Portrait": "9:16",
            "4:3 Standard": "4:3"
        }
        aspect_ratio_display = st.selectbox(
            "Aspect Ratio",
            options=list(aspect_ratio_options.keys()),
            index=0
        )
        aspect_ratio = aspect_ratio_options[aspect_ratio_display]

        # Generate button
        if st.button("✨ Generate with Imagen 4", type="primary", use_container_width=True):
            if not style_prompt:
                st.error("⚠️ Please describe the visual style you want to generate")
            else:
                with st.spinner("Generating style reference with Imagen 4..."):
                    try:
                        # Call API
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/styles/generate",
                            json={
                                "prompt": style_prompt,
                                "aspect_ratio": aspect_ratio,
                                "save_to_database": False
                            },
                            timeout=120
                        )

                        if response.status_code == 200:
                            result = response.json().get('data', {})

                            st.session_state.generated_style_image = result.get('image_base64')
                            st.session_state.generated_style_suffix = result.get('style_suffix')

                            if result.get('success'):
                                st.success(f"✅ Style reference generated with {result.get('model', 'Imagen')}!")
                            else:
                                st.info(f"ℹ️ {result.get('note', 'Placeholder generated (Imagen not configured)')}")

                        else:
                            st.error("❌ Style generation failed")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with imagen_col2:
        st.markdown("**Generated Style:**")

        # Display generated image
        if st.session_state.generated_style_image:
            import base64
            from io import BytesIO

            # Decode base64 image
            image_data = base64.b64decode(st.session_state.generated_style_image)

            # Display image
            st.image(image_data, caption="AI-Generated Style Reference", use_container_width=True)

            # Display extracted style suffix
            if st.session_state.generated_style_suffix:
                st.markdown("**🎬 Extracted Style Suffix:**")
                st.code(st.session_state.generated_style_suffix, language=None)

            st.markdown("---")

            # Option to save as style
            save_style_name = st.text_input(
                "Save this style as:",
                placeholder="e.g., 'My Cyberpunk Look'",
                key="save_generated_style_name"
            )

            if st.button("💾 Use as Anchor & Save Style", type="secondary", use_container_width=True):
                if not save_style_name:
                    st.error("⚠️ Please enter a name for the style")
                else:
                    with st.spinner(f"Saving '{save_style_name}' to database..."):
                        try:
                            # Call API to save
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/styles/generate",
                                json={
                                    "prompt": style_prompt,
                                    "style_name": save_style_name,
                                    "aspect_ratio": aspect_ratio,
                                    "save_to_database": True
                                },
                                timeout=120
                            )

                            if response.status_code == 200:
                                result = response.json().get('data', {})
                                if result.get('saved'):
                                    st.success(f"✅ {result.get('message')}")
                                    # Clear cache
                                    st.session_state.available_styles = []
                                    st.balloons()
                                else:
                                    st.warning(f"⚠️ {result.get('message')}")
                            else:
                                st.error("❌ Failed to save style")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👈 Enter a description and click **Generate** to create a style reference image")

    # ================================
    # BOTTOM: SCENE IMAGES GALLERY
    # ================================
    st.markdown("---")
    st.subheader("📁 Scene Images Gallery")
    st.caption("Upload reference images for specific scenes (optional)")

    scene_col1, scene_col2 = st.columns([2, 1])

    with scene_col1:
        visual_files = st.file_uploader(
            "Upload scene images",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Upload images for each scene. Naming: scene01.png, scene02.png, etc.",
            key="scene_images_uploader"
        )

        if visual_files:
            st.success(f"✅ {len(visual_files)} image(s) uploaded")

            st.markdown("#### Gallery View:")

            # Display in grid
            cols_per_row = 3
            for i in range(0, len(visual_files), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(visual_files):
                        file = visual_files[idx]
                        with col:
                            st.image(file, caption=f"📁 {file.name}", use_container_width=True)
                            st.caption(f"Size: {file.size / 1024:.1f} KB")

    with scene_col2:
        st.markdown("**Scene Guidelines:**")
        st.caption("• Format: PNG, JPG, WEBP")
        st.caption("• Resolution: 1920x1080+")
        st.caption("• Aspect Ratio: 16:9")
        st.caption("• Max: 10 MB per file")

        st.markdown("---")
        st.markdown("**Naming Convention:**")
        st.code("scene01.png\nscene02.png\nscene03.png", language=None)

        if visual_files:
            st.markdown("---")
            if st.button("📊 View Mapping Table", use_container_width=True):
                mapping_data = []
                for idx, file in enumerate(visual_files, 1):
                    mapping_data.append({
                        "Scene #": idx,
                        "Filename": file.name,
                        "Size": f"{file.size / 1024:.1f} KB"
                    })
                st.dataframe(mapping_data, use_container_width=True, hide_index=True)

# ================================
# TAB 4: PRODUCTION
# ================================
with tab4:
    st.header("🎬 Video Prompt Generation")
    st.markdown("Generate platform-optimized prompts for **Google Veo** and **Runway Gen-4**")

    # Session state for prompts
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = None
    if 'validation_stats' not in st.session_state:
        st.session_state.validation_stats = None

    # Top controls
    control_col1, control_col2, control_col3 = st.columns([2, 2, 1])

    with control_col1:
        # Style selector (from Tab 3)
        style_options_tab4 = ["None"] + [style["name"] for style in st.session_state.available_styles]
        selected_style_tab4 = st.selectbox(
            "🎨 Apply Visual Style",
            options=style_options_tab4,
            help="Choose a style preset to apply to all prompts"
        )

    with control_col2:
        validate_prompts = st.checkbox(
            "🔍 Validate with QC Refiner (Agent 8)",
            value=True,
            help="Auto-correct length, forbidden keywords, and quality issues"
        )

    with control_col3:
        st.metric("Scenes", len(st.session_state.processed_scenes) if 'processed_scenes' in st.session_state else 0)

    st.markdown("---")

    # Generate button
    if st.button("🎬 Generate Video Production Plan", use_container_width=True, type="primary"):
        if 'processed_scenes' not in st.session_state or len(st.session_state.processed_scenes) == 0:
            st.error("⚠️ No scenes found! Please process audio in Tab 2 first.")
        else:
            with st.spinner("Generating prompts with Agents 6, 7, and 8..."):
                try:
                    # Prepare request
                    request_data = {
                        "scenes": st.session_state.processed_scenes,
                        "style_name": selected_style_tab4 if selected_style_tab4 != "None" else None,
                        "validate": validate_prompts
                    }

                    # Call API
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/prompts/generate",
                        json=request_data,
                        timeout=120
                    )

                    if response.status_code == 200:
                        result = response.json()
                        data = result.get('data', {})

                        st.session_state.generated_prompts = data
                        st.session_state.validation_stats = data.get('validation_stats')

                        st.success(f"✅ {result.get('message', 'Prompts generated successfully!')}")

                        if st.session_state.validation_stats:
                            stats = st.session_state.validation_stats
                            st.info(f"📊 Validation: {stats['valid']} valid, {stats['corrected']} corrected, {stats['errors']} errors")

                        st.balloons()
                    else:
                        st.error(f"❌ API Error: {response.text}")

                except Exception as e:
                    st.error(f"❌ Failed to generate prompts: {str(e)}")

    st.markdown("---")

    # Display prompts if generated
    if st.session_state.generated_prompts:
        veo_prompts = st.session_state.generated_prompts.get('veo_prompts', [])
        runway_prompts = st.session_state.generated_prompts.get('runway_prompts', [])
        style_used = st.session_state.generated_prompts.get('style_used')

        # Header with download button
        header_col1, header_col2 = st.columns([3, 1])

        with header_col1:
            st.subheader(f"📋 Production Script ({len(veo_prompts)} scenes)")
            if style_used:
                st.caption(f"Style: **{style_used}**")

        with header_col2:
            # Download button
            if st.button("💾 Download Script", use_container_width=True):
                # Build production script
                script_lines = []
                script_lines.append("=" * 80)
                script_lines.append("VIDEO PRODUCTION SCRIPT")
                script_lines.append("=" * 80)
                script_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if style_used:
                    script_lines.append(f"Style: {style_used}")
                script_lines.append(f"\nTotal Scenes: {len(veo_prompts)}")
                script_lines.append("\n" + "=" * 80 + "\n")

                for i in range(len(veo_prompts)):
                    veo = veo_prompts[i]
                    runway = runway_prompts[i]

                    script_lines.append(f"\n{'=' * 80}")
                    script_lines.append(f"SCENE {i+1}")
                    script_lines.append(f"{'=' * 80}")

                    if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes):
                        scene = st.session_state.processed_scenes[i]
                        script_lines.append(f"\nTiming: {scene.get('start', 0):.2f}s - {scene.get('end', 0):.2f}s")
                        script_lines.append(f"Duration: {scene.get('duration', 0):.2f}s")
                        script_lines.append(f"Energy: {scene.get('energy', 'N/A')}")
                        script_lines.append(f"Type: {scene.get('type', 'N/A')}")

                    script_lines.append(f"\n--- GOOGLE VEO (Narrative) ---")
                    script_lines.append(f"Prompt: {veo.get('prompt', '')}")
                    if veo.get('negative'):
                        script_lines.append(f"Negative: {veo.get('negative', '')}")
                    if veo.get('status'):
                        script_lines.append(f"Status: {veo.get('status', '').upper()}")
                    if veo.get('corrections_made'):
                        script_lines.append(f"Corrections: {', '.join(veo.get('corrections_made', []))}")

                    script_lines.append(f"\n--- RUNWAY GEN-4 (Modular) ---")
                    script_lines.append(f"Prompt: {runway.get('prompt', '')}")
                    if runway.get('negative'):
                        script_lines.append(f"Negative: {runway.get('negative', '')}")
                    if runway.get('status'):
                        script_lines.append(f"Status: {runway.get('status', '').upper()}")
                    if runway.get('corrections_made'):
                        script_lines.append(f"Corrections: {', '.join(runway.get('corrections_made', []))}")

                    script_lines.append("")

                script_text = "\n".join(script_lines)

                st.download_button(
                    label="📥 Download Production Script (.txt)",
                    data=script_text,
                    file_name=f"production_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        st.markdown("---")

        # Display each scene's prompts
        for i in range(len(veo_prompts)):
            veo = veo_prompts[i]
            runway = runway_prompts[i]

            # Scene header
            with st.expander(f"🎬 Scene {i+1} - {veo.get('duration', 0):.1f}s", expanded=(i < 3)):
                # Scene metadata (if available)
                if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes):
                    scene = st.session_state.processed_scenes[i]
                    meta_col1, meta_col2, meta_col3 = st.columns(3)
                    with meta_col1:
                        st.caption(f"⏱️ {scene.get('start', 0):.2f}s - {scene.get('end', 0):.2f}s")
                    with meta_col2:
                        st.caption(f"⚡ {scene.get('energy', 'N/A')}")
                    with meta_col3:
                        st.caption(f"🎭 {scene.get('type', 'N/A')}")

                # Veo prompt
                st.markdown("**🎥 Google Veo (Narrative)**")
                st.markdown("*Click the copy icon in the top-right corner to copy to clipboard*")
                st.code(
                    veo.get('prompt', ''),
                    language='text'
                )

                # Show status if validated
                if veo.get('status'):
                    status = veo.get('status', '')
                    if status == 'valid':
                        st.success(f"✅ Valid ({len(veo.get('prompt', ''))} chars)")
                    elif status == 'corrected':
                        st.warning(f"⚠️ Corrected: {', '.join(veo.get('corrections_made', []))}")
                    elif status == 'error':
                        st.error(f"❌ Issues: {', '.join(veo.get('issues_found', []))}")

                # Mark as Gold Standard button (Feedback Loop)
                if st.button(f"⭐ Mark as Gold Standard", key=f"gold_veo_{i}", help="Save this prompt for Few-Shot Learning"):
                    with st.spinner("Saving to learning database..."):
                        try:
                            # Get scene info for description
                            scene_desc = f"Scene {i+1}"
                            if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes):
                                scene = st.session_state.processed_scenes[i]
                                scene_desc = f"{scene.get('type', 'Scene')} at {scene.get('start', 0):.1f}s"

                            # Call API
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/prompts/mark-gold-standard",
                                json={
                                    "model": "veo",
                                    "prompt": veo.get('prompt', ''),
                                    "scene_description": scene_desc,
                                    "energy": scene.get('energy', 'medium') if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes) else 'medium'
                                },
                                timeout=30
                            )

                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ {result.get('message', 'Added to learning database!')}")
                                st.info("🧠 Future prompt generations will learn from this example")
                            else:
                                st.error("❌ Failed to save")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

                st.markdown("---")

                # Runway prompt
                st.markdown("**🚀 Runway Gen-4 (Modular)**")
                st.markdown("*Click the copy icon in the top-right corner to copy to clipboard*")
                st.code(
                    runway.get('prompt', ''),
                    language='text'
                )

                # Show status if validated
                if runway.get('status'):
                    status = runway.get('status', '')
                    if status == 'valid':
                        st.success(f"✅ Valid ({len(runway.get('prompt', ''))} chars)")
                    elif status == 'corrected':
                        st.warning(f"⚠️ Corrected: {', '.join(runway.get('corrections_made', []))}")
                    elif status == 'error':
                        st.error(f"❌ Issues: {', '.join(runway.get('issues_found', []))}")

                # Mark as Gold Standard button (Feedback Loop)
                if st.button(f"⭐ Mark as Gold Standard", key=f"gold_runway_{i}", help="Save this prompt for Few-Shot Learning"):
                    with st.spinner("Saving to learning database..."):
                        try:
                            # Get scene info for description
                            scene_desc = f"Scene {i+1}"
                            if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes):
                                scene = st.session_state.processed_scenes[i]
                                scene_desc = f"{scene.get('type', 'Scene')} at {scene.get('start', 0):.1f}s"

                            # Call API
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/prompts/mark-gold-standard",
                                json={
                                    "model": "runway",
                                    "prompt": runway.get('prompt', ''),
                                    "scene_description": scene_desc,
                                    "energy": scene.get('energy', 'medium') if 'processed_scenes' in st.session_state and i < len(st.session_state.processed_scenes) else 'medium'
                                },
                                timeout=30
                            )

                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ {result.get('message', 'Added to learning database!')}")
                                st.info("🧠 Future prompt generations will learn from this example")
                            else:
                                st.error("❌ Failed to save")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

    else:
        st.info("👆 Click **Generate Video Production Plan** to create platform-optimized prompts for all scenes.")

# ================================
# TAB 5: POST-PRODUCTION & DISTRIBUTION
# ================================
with tab5:
    st.header("✂️ Post-Production & Distribution")
    st.markdown("CapCut editing guide + YouTube upload package")

    # Session state for guides
    if 'capcut_guide' not in st.session_state:
        st.session_state.capcut_guide = None
    if 'youtube_metadata' not in st.session_state:
        st.session_state.youtube_metadata = None
    if 'thumbnail_prompt' not in st.session_state:
        st.session_state.thumbnail_prompt = None

    col1, col2 = st.columns([1, 1])

    # ================================
    # LEFT COLUMN: CapCut Editing Guide
    # ================================
    with col1:
        st.subheader("📹 CapCut Editing Guide")
        st.markdown("Generate step-by-step editing instructions based on your scenes")

        # Generate button
        if st.button("🎬 Generate CapCut Guide", use_container_width=True, type="primary"):
            if 'processed_scenes' not in st.session_state or len(st.session_state.processed_scenes) == 0:
                st.error("⚠️ No scenes found! Please process audio in Tab 2 first.")
            else:
                with st.spinner("Generating CapCut editing guide..."):
                    try:
                        # Get total audio duration if available
                        audio_duration = None
                        if st.session_state.processed_scenes:
                            last_scene = st.session_state.processed_scenes[-1]
                            audio_duration = last_scene.get('end', 0)

                        # Prepare request
                        request_data = {
                            "scenes": st.session_state.processed_scenes,
                            "audio_duration": audio_duration
                        }

                        # Call API
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/capcut/generate-guide",
                            json=request_data,
                            timeout=60
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.capcut_guide = data.get('guide')

                            st.success(f"✅ {result.get('message', 'Guide generated!')}")
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Failed to generate guide: {str(e)}")

        st.markdown("---")

        # Display guide if generated
        if st.session_state.capcut_guide:
            st.markdown("### 📋 Your Editing Guide")

            # Display markdown guide
            st.markdown(st.session_state.capcut_guide)

            # Download button
            st.download_button(
                label="💾 Download CapCut Guide (.md)",
                data=st.session_state.capcut_guide,
                file_name=f"capcut_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.info("👆 Click **Generate CapCut Guide** to create your personalized editing instructions")

    # ================================
    # RIGHT COLUMN: YouTube Package
    # ================================
    with col2:
        st.subheader("📺 YouTube Upload Package")
        st.markdown("Generate viral metadata + thumbnail prompt")

        # Input fields
        final_song_title = st.text_input(
            "Final Song Title",
            value=st.session_state.get('song_title', ''),
            placeholder="e.g., Midnight Dreams"
        )

        final_artist = st.text_input(
            "Artist Name",
            value=st.session_state.get('artist', ''),
            placeholder="e.g., Phoenix"
        )

        yt_col1, yt_col2 = st.columns(2)

        with yt_col1:
            genre_input = st.text_input("Genre (optional)", placeholder="e.g., Electronic")

        with yt_col2:
            mood_input = st.text_input("Mood (optional)", placeholder="e.g., Energetic")

        # Style selector
        style_options_yt = ["None"] + [style["name"] for style in st.session_state.available_styles]
        selected_style_yt = st.selectbox(
            "Visual Style (optional)",
            options=style_options_yt,
            help="Select the visual style used in your video"
        )

        # Generate button
        if st.button("🚀 Generate YouTube Package", use_container_width=True, type="primary"):
            if not final_song_title or not final_artist:
                st.error("⚠️ Please enter both song title and artist name")
            else:
                with st.spinner("Generating YouTube package with AI..."):
                    try:
                        # Prepare request for metadata
                        metadata_request = {
                            "song_title": final_song_title,
                            "artist": final_artist,
                            "genre": genre_input if genre_input else None,
                            "mood": mood_input if mood_input else None,
                            "style_name": selected_style_yt if selected_style_yt != "None" else None
                        }

                        # Call metadata API
                        metadata_response = requests.post(
                            f"{API_BASE_URL}/api/v1/youtube/generate-metadata",
                            json=metadata_request,
                            timeout=60
                        )

                        # Call thumbnail API
                        thumbnail_request = {
                            "song_title": final_song_title,
                            "artist": final_artist,
                            "style_name": selected_style_yt if selected_style_yt != "None" else None,
                            "mood": mood_input if mood_input else None
                        }

                        thumbnail_response = requests.post(
                            f"{API_BASE_URL}/api/v1/youtube/generate-thumbnail",
                            json=thumbnail_request,
                            timeout=60
                        )

                        if metadata_response.status_code == 200 and thumbnail_response.status_code == 200:
                            metadata_result = metadata_response.json()
                            thumbnail_result = thumbnail_response.json()

                            st.session_state.youtube_metadata = metadata_result.get('data', {})
                            st.session_state.thumbnail_prompt = thumbnail_result.get('data', {}).get('prompt')

                            st.success("✅ YouTube package generated!")
                            st.balloons()
                        else:
                            st.error(f"❌ API Error")

                    except Exception as e:
                        st.error(f"❌ Failed to generate package: {str(e)}")

        st.markdown("---")

        # Display YouTube package if generated
        if st.session_state.youtube_metadata:
            metadata = st.session_state.youtube_metadata

            st.markdown("### 📦 Your YouTube Package")

            # Title
            st.markdown("**📌 Title** (click to copy)")
            st.code(metadata.get('title', ''), language=None)

            # Description
            st.markdown("**📝 Description**")
            st.text_area(
                "Description",
                value=metadata.get('description', ''),
                height=200,
                key="yt_description",
                label_visibility="collapsed"
            )

            # Tags
            st.markdown("**🏷️ Tags**")
            tags_text = ", ".join(metadata.get('tags', []))
            st.code(tags_text, language=None)

            # Hashtags
            if metadata.get('hashtags'):
                st.markdown("**#️⃣ Hashtags**")
                hashtags_text = " ".join(metadata.get('hashtags', []))
                st.code(hashtags_text, language=None)

            st.markdown("---")

            # Thumbnail prompt
            if st.session_state.thumbnail_prompt:
                st.markdown("**🖼️ Thumbnail Prompt** (for Imagen 3 / Midjourney)")
                st.text_area(
                    "Thumbnail Prompt",
                    value=st.session_state.thumbnail_prompt,
                    height=150,
                    key="thumbnail_prompt_display",
                    label_visibility="collapsed"
                )

                st.caption("Use this prompt with Imagen 3, Midjourney, or DALL-E to generate your thumbnail")

            # Download all as text file
            package_text = f"""YOUTUBE UPLOAD PACKAGE
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==================== TITLE ====================
{metadata.get('title', '')}

==================== DESCRIPTION ====================
{metadata.get('description', '')}

==================== TAGS ====================
{tags_text}

==================== HASHTAGS ====================
{hashtags_text if metadata.get('hashtags') else 'N/A'}

==================== THUMBNAIL PROMPT ====================
{st.session_state.thumbnail_prompt if st.session_state.thumbnail_prompt else 'N/A'}
"""

            st.download_button(
                label="💾 Download Complete Package (.txt)",
                data=package_text,
                file_name=f"youtube_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:
            st.info("👆 Fill in the details and click **Generate YouTube Package**")

# ================================
# TAB 6: DOKU-STUDIO
# ================================
with tab6:
    st.header("📽️ Doku-Studio - Netflix-Style Documentary Generator")
    st.markdown("**Clone any documentary's style and create 15-minute scripts on any topic**")
    st.markdown("---")

    # Session state for documentary
    if 'doc_style_template' not in st.session_state:
        st.session_state.doc_style_template = None
    if 'doc_script' not in st.session_state:
        st.session_state.doc_script = None

    col1, col2 = st.columns([1, 1])

    # ================================
    # LEFT: STYLE CLONING (Agent 12)
    # ================================
    with col1:
        st.subheader("🔍 Style Analyzer (Reverse Engineering)")
        st.markdown("**Analyze a reference documentary to extract its style template**")

        with st.expander("📖 How Style Cloning Works", expanded=False):
            st.markdown("""
            **The Reverse Engineering Process:**
            1. Paste a YouTube URL of your reference documentary (e.g., Vox, BBC, Vice)
            2. Agent 12 extracts the transcript automatically
            3. AI analyzes pacing, narrative style, and tone
            4. Generates a comprehensive "Style Template"
            5. Use this template to clone the style for your own topic

            **What gets analyzed:**
            - Pacing (words per minute, cut frequency)
            - Narrative style (informative, dramatic, conversational)
            - Mood and tone
            - Visual style and color palette
            - B-Roll frequency and suggestions
            - Key storytelling patterns
            """)

        st.markdown("---")

        # YouTube URL input
        youtube_url = st.text_input(
            "YouTube URL of Reference Documentary",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the URL of a documentary you want to clone the style from"
        )

        # Analyze button
        if st.button("🔬 Analyze Style", type="primary", use_container_width=True):
            if not youtube_url:
                st.error("⚠️ Please enter a YouTube URL")
            else:
                with st.spinner("Agent 12 analyzing documentary style..."):
                    try:
                        # Call API
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/analyze-style",
                            json={"video_url": youtube_url},
                            timeout=120
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.doc_style_template = data

                            st.success(f"✅ {result.get('message', 'Style extracted!')}")
                            st.balloons()
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

        # Display style template if analyzed
        if st.session_state.doc_style_template:
            st.markdown("### 📋 Extracted Style Template")

            template = st.session_state.doc_style_template

            # Template name
            st.info(f"**{template.get('template_name', 'Custom Style')}**")

            # Pacing
            st.markdown("**⏱️ Pacing:**")
            pacing = template.get('pacing', {})
            st.caption(f"• {pacing.get('words_per_minute', 'N/A')} WPM")
            st.caption(f"• {pacing.get('estimated_duration_minutes', 'N/A')} minutes estimated")
            st.caption(f"• {pacing.get('cut_frequency', 'N/A')}")

            # Tone
            st.markdown("**🎭 Tone:**")
            tone = template.get('tone', {})
            st.caption(f"• Style: {tone.get('narrative_style', 'N/A')}")
            st.caption(f"• Mood: {tone.get('mood', 'N/A')}")
            st.caption(f"• Voice: {tone.get('narrator_voice', 'N/A')}")

            # Visual style
            st.markdown("**🎨 Visual Style:**")
            visual = template.get('visual_style', {})
            st.caption(f"• Colors: {visual.get('color_palette', 'N/A')}")
            st.caption(f"• B-Roll: {visual.get('b_roll_frequency', 'N/A')}")

            # Keywords
            if template.get('keywords'):
                st.markdown("**🔑 Keywords:**")
                st.caption(", ".join(template.get('keywords', [])[:10]))

            # Download as JSON
            import json
            template_json = json.dumps(template, indent=2)
            st.download_button(
                label="💾 Download Style Template (JSON)",
                data=template_json,
                file_name=f"style_template_{template.get('template_name', 'custom').replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

        else:
            st.info("👆 Enter a YouTube URL and click **Analyze Style** to extract the documentary's template")

    # ================================
    # RIGHT: STORY DEVELOPMENT (Agent 13)
    # ================================
    with col2:
        st.subheader("✍️ Story Architect (3-Act Structure)")
        st.markdown("**Generate a complete 15-minute documentary script**")

        with st.expander("📖 How Script Generation Works", expanded=False):
            st.markdown("""
            **The 3-Act Structure:**
            - **Act 1: The Hook** (0-2 min) - Grab attention, establish stakes
            - **Act 2: The Conflict/Journey** (2-10 min) - Dive deep, build tension
            - **Act 3: The Resolution** (10-15 min) - Provide answers, conclude

            **What you get:**
            - Complete narrator script (~2250 words)
            - Chapter breakdown with timings
            - B-Roll suggestions for each chapter
            - Actionable production instructions

            **Optional:** Apply the style template from Agent 12 to clone the style!
            """)

        st.markdown("---")

        # Topic input
        doc_topic = st.text_area(
            "Documentary Topic",
            placeholder="e.g., 'The Rise of Artificial Intelligence' or 'The Future of Climate Change'",
            height=80,
            help="Enter the main topic of your documentary"
        )

        # Duration
        doc_duration = st.slider(
            "Duration (minutes)",
            min_value=5,
            max_value=30,
            value=15,
            help="Total documentary duration"
        )

        # Use style template checkbox
        use_template = st.checkbox(
            "🎨 Apply Style Template (from left)",
            value=bool(st.session_state.doc_style_template),
            disabled=not st.session_state.doc_style_template,
            help="Clone the style from the analyzed documentary"
        )

        # Generate button
        if st.button("🎬 Generate 15-Minute Script", type="primary", use_container_width=True):
            if not doc_topic:
                st.error("⚠️ Please enter a documentary topic")
            else:
                with st.spinner("Agent 13 creating 3-act structure with Gemini Pro..."):
                    try:
                        # Prepare request
                        request_data = {
                            "topic": doc_topic,
                            "duration_minutes": doc_duration,
                            "style_template": st.session_state.doc_style_template if use_template else None
                        }

                        # Call API
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/generate-script",
                            json=request_data,
                            timeout=180
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.doc_script = data

                            st.success(f"✅ {result.get('message', 'Script generated!')}")
                            st.balloons()
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

        # Display script if generated
        if st.session_state.doc_script:
            st.markdown("### 📜 Generated Documentary Script")

            script = st.session_state.doc_script

            # Title and logline
            st.info(f"**{script.get('title', 'Untitled')}**\n\n{script.get('logline', '')}")

            # Stats
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.metric("Duration", f"{script.get('total_duration_minutes', 0)} min")
            with stats_col2:
                st.metric("Word Count", f"{script.get('total_word_count', 0)}")

            # 3-Act Structure
            st.markdown("**📖 3-Act Structure:**")
            structure = script.get('structure', {})
            for act_key, act_data in structure.items():
                with st.expander(f"{act_data.get('title', act_key)} - {act_data.get('duration_range', 'N/A')}", expanded=False):
                    st.markdown(f"**Objective:** {act_data.get('objective', '')}")
                    st.markdown("**Key Points:**")
                    for point in act_data.get('key_points', []):
                        st.caption(f"• {point}")

            # Chapters
            st.markdown("**🎬 Chapters:**")
            chapters = script.get('chapters', [])
            for chapter in chapters:
                with st.expander(
                    f"Chapter {chapter.get('chapter_number')}: {chapter.get('title')} ({chapter.get('start_time')} - {chapter.get('end_time')})",
                    expanded=False
                ):
                    st.markdown("**📝 Narration:**")
                    st.text_area(
                        "Narrator Script",
                        value=chapter.get('narration', ''),
                        height=200,
                        key=f"chapter_{chapter.get('chapter_number')}_narration",
                        label_visibility="collapsed"
                    )

                    st.markdown("**🎥 B-Roll Shots:**")
                    for shot in chapter.get('b_roll_shots', []):
                        st.caption(f"• {shot}")

                    if chapter.get('key_visuals'):
                        st.markdown(f"**🖼️ Key Visuals:** {chapter.get('key_visuals')}")

            # Download script
            import json
            script_json = json.dumps(script, indent=2)
            st.download_button(
                label="💾 Download Complete Script (JSON)",
                data=script_json,
                file_name=f"documentary_script_{script.get('title', 'untitled').replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

            # Export as text file
            script_text_lines = []
            script_text_lines.append("=" * 80)
            script_text_lines.append(f"DOCUMENTARY SCRIPT: {script.get('title', 'Untitled')}")
            script_text_lines.append("=" * 80)
            script_text_lines.append(f"\nLogline: {script.get('logline', '')}")
            script_text_lines.append(f"Duration: {script.get('total_duration_minutes', 0)} minutes")
            script_text_lines.append(f"Word Count: {script.get('total_word_count', 0)}\n")
            script_text_lines.append("=" * 80)

            for chapter in chapters:
                script_text_lines.append(f"\n\n{'=' * 80}")
                script_text_lines.append(f"CHAPTER {chapter.get('chapter_number')}: {chapter.get('title')}")
                script_text_lines.append(f"Time: {chapter.get('start_time')} - {chapter.get('end_time')}")
                script_text_lines.append("=" * 80)
                script_text_lines.append(f"\n{chapter.get('narration', '')}\n")
                script_text_lines.append("\nB-ROLL:")
                for shot in chapter.get('b_roll_shots', []):
                    script_text_lines.append(f"- {shot}")

            script_text = "\n".join(script_text_lines)

            st.download_button(
                label="📄 Download as Text File",
                data=script_text,
                file_name=f"documentary_script_{script.get('title', 'untitled').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:
            st.info("👆 Enter a topic and click **Generate Script** to create your documentary")

    # ================================
    # PRODUCTION WORKFLOW (Agents 14-17)
    # ================================
    if st.session_state.doc_script:
        st.markdown("---")
        st.header("🎙️ Production Workflow")
        st.markdown("**Complete your documentary with voiceover, fact-checking, stock footage, and editing timeline**")

        # Session state for production assets
        if 'doc_voiceover_text' not in st.session_state:
            st.session_state.doc_voiceover_text = None
        if 'doc_fact_report' not in st.session_state:
            st.session_state.doc_fact_report = None
        if 'doc_stock_footage' not in st.session_state:
            st.session_state.doc_stock_footage = None
        if 'doc_xml_content' not in st.session_state:
            st.session_state.doc_xml_content = None

        prod_col1, prod_col2 = st.columns([1, 1])

        # ================================
        # LEFT COLUMN: VOICEOVER & FACT CHECK
        # ================================
        with prod_col1:
            st.subheader("🎙️ Voiceover Preparation (Agent 14)")

            # Mode selection
            voiceover_mode = st.radio(
                "Generation Mode",
                options=["manual", "api"],
                format_func=lambda x: "🖐️ Manual (Download for ElevenLabs)" if x == "manual" else "🤖 API (Auto - ElevenLabs)",
                help="Manual: Download script text for manual upload to ElevenLabs web interface\nAPI: Automatic generation (requires ElevenLabs API key)"
            )

            # Prepare voiceover button
            if st.button("📝 Prepare Voiceover Script", use_container_width=True):
                with st.spinner("Agent 14 preparing voiceover..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/prepare-voiceover",
                            json={
                                "script": st.session_state.doc_script,
                                "mode": voiceover_mode
                            },
                            timeout=60
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.doc_voiceover_text = data.get('script_text')

                            st.success(f"✅ {result.get('message')}")

                            # Display stats
                            col_stat1, col_stat2 = st.columns(2)
                            with col_stat1:
                                st.metric("Word Count", data.get('word_count', 0))
                            with col_stat2:
                                st.metric("Estimated Duration", f"{data.get('duration_estimate', 0)} min")
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Download voiceover script (manual mode)
            if st.session_state.doc_voiceover_text and voiceover_mode == "manual":
                st.markdown("---")
                st.markdown("**📥 Manual Workflow:**")

                # Instructions
                with st.expander("📖 How to use ElevenLabs (Manual Mode)", expanded=False):
                    st.markdown("""
                    **Step-by-step:**
                    1. Download the script text below
                    2. Go to https://elevenlabs.io
                    3. Select a professional narrator voice (recommended: "Josh" or "Bella")
                    4. Paste the script into the text input
                    5. Click "Generate" and download the MP3
                    6. Upload the finished MP3 below

                    **Recommended Settings:**
                    - Stability: 50-60%
                    - Clarity: 70-80%
                    - Style Exaggeration: 0-10%
                    """)

                # Download button
                st.download_button(
                    label="📥 Download Script for ElevenLabs",
                    data=st.session_state.doc_voiceover_text,
                    file_name=f"voiceover_script_{st.session_state.doc_script.get('title', 'documentary').replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    type="primary"
                )

                # Upload finished audio
                st.markdown("**📤 Upload Finished Audio:**")
                uploaded_audio = st.file_uploader(
                    "Upload MP3/WAV from ElevenLabs",
                    type=["mp3", "wav"],
                    help="Upload the generated voiceover audio file"
                )

                if uploaded_audio:
                    st.success(f"✅ Audio uploaded: {uploaded_audio.name}")
                    st.audio(uploaded_audio)

            st.markdown("---")

            # Fact Check section (Agent 15)
            st.subheader("🔍 Fact Checker (Agent 15)")

            check_mode = st.selectbox(
                "Check Mode",
                options=["critical", "full"],
                format_func=lambda x: "🎯 Critical (Numbers, Dates, Names)" if x == "critical" else "📋 Full (All Claims)",
                help="Critical: Check only verifiable facts\nFull: Check all statements"
            )

            if st.button("🔬 Verify Facts", use_container_width=True):
                with st.spinner("Agent 15 fact-checking with Gemini + Google Search..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/fact-check",
                            json={
                                "script": st.session_state.doc_script,
                                "check_mode": check_mode
                            },
                            timeout=120
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.doc_fact_report = data.get('fact_report')

                            # Display result
                            issues_count = data.get('issues_found', 0)

                            if issues_count > 0:
                                st.warning(f"⚠️ {issues_count} critical issues found!")
                            else:
                                st.success("✅ All facts verified!")

                            # Stats
                            col_stat1, col_stat2 = st.columns(2)
                            with col_stat1:
                                st.metric("Claims Checked", data.get('checks_performed', 0))
                            with col_stat2:
                                st.metric("Issues Found", issues_count, delta_color="inverse")
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Display fact report
            if st.session_state.doc_fact_report:
                st.markdown("---")
                st.markdown("**📋 Fact-Check Report:**")

                with st.expander("📄 View Full Report", expanded=True):
                    st.markdown(st.session_state.doc_fact_report)

                # Download report
                st.download_button(
                    label="💾 Download Fact-Check Report",
                    data=st.session_state.doc_fact_report,
                    file_name=f"fact_check_report_{st.session_state.doc_script.get('title', 'documentary').replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

        # ================================
        # RIGHT COLUMN: STOCK FOOTAGE & XML
        # ================================
        with prod_col2:
            st.subheader("🎥 Stock Footage Scout (Agent 16)")

            media_type = st.radio(
                "Media Type",
                options=["videos", "photos"],
                format_func=lambda x: "🎬 Stock Videos" if x == "videos" else "🖼️ Stock Photos",
                horizontal=True
            )

            results_per_keyword = st.slider(
                "Results per Keyword",
                min_value=1,
                max_value=5,
                value=3,
                help="Number of stock footage results to return per B-roll keyword"
            )

            if st.button("🔍 Find Stock Footage", use_container_width=True):
                with st.spinner(f"Agent 16 searching Pexels for free {media_type}..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/find-stock-footage",
                            json={
                                "script": st.session_state.doc_script,
                                "media_type": media_type,
                                "results_per_keyword": results_per_keyword
                            },
                            timeout=60
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            st.session_state.doc_stock_footage = data

                            st.success(f"✅ Found {data.get('total_found', 0)} {media_type}")
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Display stock footage results
            if st.session_state.doc_stock_footage:
                st.markdown("---")
                st.markdown(f"**🎬 Stock {media_type.title()}:**")

                results = st.session_state.doc_stock_footage.get('results', [])

                # Display in grid
                for i in range(0, len(results), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if i + j < len(results):
                            item = results[i + j]
                            with col:
                                with st.container():
                                    if item.get('thumbnail'):
                                        st.image(item['thumbnail'], use_container_width=True)

                                    st.caption(f"**{item.get('title', 'Untitled')}**")
                                    st.caption(f"🔑 {item.get('search_keyword', '')}")

                                    if media_type == "videos":
                                        st.caption(f"⏱️ {item.get('duration', 0)}s")

                                    st.caption(f"📷 {item.get('photographer', 'Unknown')}")

                                    if item.get('download_url'):
                                        st.link_button(
                                            "⬇️ Download",
                                            item['download_url'],
                                            use_container_width=True
                                        )

                # Export URLs
                st.markdown("---")
                footage_urls = "\n".join([f"{item.get('title')}: {item.get('download_url')}" for item in results if item.get('download_url')])

                st.download_button(
                    label="💾 Export All URLs (Text)",
                    data=footage_urls,
                    file_name=f"stock_footage_urls_{media_type}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            st.markdown("---")

            # XML Generation (Agent 17)
            st.subheader("🎬 Timeline Generator (Agent 17)")
            st.markdown("**Generate FCPXML for DaVinci Resolve / Premiere Pro**")

            with st.expander("ℹ️ About FCPXML", expanded=False):
                st.markdown("""
                **FCPXML (Final Cut Pro XML)** is an interchange format supported by:
                - DaVinci Resolve
                - Adobe Premiere Pro
                - Final Cut Pro
                - Avid Media Composer

                **What gets generated:**
                - Track 1: Voiceover narration
                - Track 2: Background music (30% volume)
                - Track 3: B-roll videos
                - Track 4: Still images
                - Chapter markers from your script

                **Note:** You'll need to add file paths to your actual assets.
                """)

            xml_format = st.selectbox(
                "Timeline Format",
                options=["fcpxml", "edl"],
                format_func=lambda x: "FCPXML (DaVinci/Premiere/FCP)" if x == "fcpxml" else "EDL (Legacy Format)"
            )

            frame_rate = st.selectbox(
                "Frame Rate",
                options=["24", "25", "30", "60"],
                format_func=lambda x: f"{x} fps",
                index=0
            )

            # Asset paths (simplified for demo)
            with st.expander("⚙️ Asset Configuration", expanded=False):
                st.markdown("**Configure asset file paths:**")

                voiceover_path = st.text_input("Voiceover Audio Path", value="/path/to/voiceover.mp3")
                music_path = st.text_input("Background Music Path", value="/path/to/music.mp3")
                voiceover_duration = st.number_input("Voiceover Duration (seconds)", value=900.0, step=10.0)
                music_duration = st.number_input("Music Duration (seconds)", value=900.0, step=10.0)

            if st.button("🎬 Generate Timeline XML", use_container_width=True, type="primary"):
                with st.spinner(f"Agent 17 generating {xml_format.upper()}..."):
                    try:
                        # Build assets dict
                        assets = {
                            "voiceover": {
                                "file_path": voiceover_path,
                                "duration": voiceover_duration
                            },
                            "music": {
                                "file_path": music_path,
                                "duration": music_duration
                            },
                            "videos": [],  # User can add manually
                            "images": []   # User can add manually
                        }

                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/documentary/generate-xml",
                            json={
                                "assets": assets,
                                "script": st.session_state.doc_script,
                                "frame_rate": frame_rate,
                                "format": xml_format
                            },
                            timeout=60
                        )

                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})

                            xml_content = data.get('xml_content') or data.get('edl_content')
                            st.session_state.doc_xml_content = xml_content

                            st.success(f"✅ {result.get('message')}")

                            # Stats
                            col_stat1, col_stat2 = st.columns(2)
                            with col_stat1:
                                st.metric("Duration", f"{data.get('timeline_duration', 0):.1f}s")
                            with col_stat2:
                                st.metric("Tracks", data.get('tracks', 0))
                        else:
                            st.error(f"❌ API Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Download XML
            if st.session_state.doc_xml_content:
                st.markdown("---")

                # Preview
                with st.expander("📄 Preview XML", expanded=False):
                    st.code(st.session_state.doc_xml_content[:1000] + "..." if len(st.session_state.doc_xml_content) > 1000 else st.session_state.doc_xml_content)

                # Download
                file_extension = "fcpxml" if xml_format == "fcpxml" else "edl"
                st.download_button(
                    label=f"💾 Download {xml_format.upper()} Timeline",
                    data=st.session_state.doc_xml_content,
                    file_name=f"documentary_timeline_{st.session_state.doc_script.get('title', 'untitled').replace(' ', '_')}.{file_extension}",
                    mime="application/xml" if xml_format == "fcpxml" else "text/plain",
                    use_container_width=True,
                    type="primary"
                )

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🎬 Music Video Agent System - Phoenix Ultimate Version | Powered by FastAPI + Streamlit + Google Gemini
</div>
""", unsafe_allow_html=True)
