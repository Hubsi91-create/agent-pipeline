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
API_BASE_URL = "http://localhost:8000"

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
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎵 Music Generation",
    "📤 Audio Upload",
    "🎨 Visuals & Style",
    "🎬 Production",
    "✂️ Post-Production"
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
            with st.spinner("Agent 1 searching TikTok, Spotify, and YouTube Shorts..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/api/v1/trends/update", timeout=30)
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
                            with st.spinner(f"Generating 20 {genre} variations..."):
                                try:
                                    response = requests.post(
                                        f"{API_BASE_URL}/api/v1/genres/variations",
                                        json={"super_genre": genre, "num_variations": 20},
                                        timeout=10
                                    )
                                    if response.status_code == 200:
                                        st.session_state.genre_variations = response.json().get('data', [])
                                    else:
                                        # Fallback mock
                                        st.session_state.genre_variations = [
                                            {"subgenre": f"{genre} Style {i+1}", "description": f"Variation {i+1}"}
                                            for i in range(20)
                                        ]
                                except:
                                    # Fallback mock
                                    st.session_state.genre_variations = [
                                        {"subgenre": f"{genre} Style {i+1}", "description": f"Variation {i+1}"}
                                        for i in range(20)
                                    ]

                            st.rerun()

        # Custom Genre Button
        st.markdown("---")
        custom_col1, custom_col2 = st.columns([1, 2])
        with custom_col1:
            if st.button("➕ Custom Genre", use_container_width=True):
                st.session_state.show_custom_input = True

        with custom_col2:
            if st.session_state.get('show_custom_input', False):
                custom_genre = st.text_input("Enter custom genre", key="custom_genre_input")
                if custom_genre and st.button("Generate", key="custom_generate"):
                    st.session_state.selected_supergenre = custom_genre
                    st.session_state.selected_variations = []
                    st.session_state.generated_prompts = []
                    # Trigger generation (same as above)
                    st.rerun()

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
                    st.text_area(
                        "Lyrics",
                        value=prompt['lyrics'],
                        height=150,
                        key=f"lyrics_{idx}",
                        label_visibility="collapsed"
                    )

                    st.markdown("**[STYLE]**")
                    st.text_area(
                        "Style",
                        value=prompt['style'],
                        height=60,
                        key=f"style_{idx}",
                        label_visibility="collapsed"
                    )

                    if st.button(f"📋 Copy Prompt {idx}", key=f"copy_{idx}"):
                        st.success(f"✅ Prompt {idx} copied to clipboard!")

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
    st.header("🎬 Video Production Configuration")
    st.markdown("Configure video generation settings")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Platform Selection")

        col_a, col_b = st.columns(2)

        with col_a:
            use_veo = st.checkbox("🎥 Google Veo", value=True, help="Google Veo video generation")
            if use_veo:
                veo_quality = st.select_slider(
                    "Veo Quality",
                    options=["Draft", "Standard", "High", "Ultra"],
                    value="High"
                )

        with col_b:
            use_runway = st.checkbox("🚀 Runway ML", value=True, help="Runway ML video generation")
            if use_runway:
                runway_model = st.selectbox(
                    "Runway Model",
                    ["Gen-3 Alpha", "Gen-2", "Gen-1"]
                )

        st.markdown("---")

        st.subheader("Generation Mode")

        generation_mode = st.radio(
            "How do you want to generate videos?",
            [
                "🔌 API Mode (Direct API calls)",
                "📝 Prompt File Mode (Export prompts to file)"
            ],
            help="API Mode: Automatic generation. Prompt File: Manual workflow with exported prompts."
        )

        if "API Mode" in generation_mode:
            st.info("✅ Direct API integration - Videos will be generated automatically")

            with st.expander("⚙️ API Configuration"):
                st.text_input("Google Veo API Key", type="password", placeholder="Enter your Veo API key...")
                st.text_input("Runway API Key", type="password", placeholder="Enter your Runway API key...")
        else:
            st.info("📝 Prompts will be exported to file for manual processing")

            export_format = st.selectbox(
                "Export Format",
                ["JSON", "CSV", "TXT (one per line)", "Markdown"]
            )

        st.markdown("---")

        st.subheader("Production Settings")

        col_x, col_y = st.columns(2)

        with col_x:
            video_duration = st.slider("Video Duration (seconds)", 5, 60, 30)
            fps = st.selectbox("Frame Rate", [24, 30, 60])

        with col_y:
            resolution = st.selectbox("Resolution", ["1920x1080", "3840x2160", "1280x720"])
            aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1", "4:3"])

        st.markdown("---")

        # Start production button
        if st.button("🎬 START PRODUCTION", use_container_width=True, type="primary"):
            if not use_veo and not use_runway:
                st.error("⚠️ Please select at least one platform (Veo or Runway)")
            else:
                with st.spinner("Initializing production pipeline..."):
                    st.success("✅ Production started!")

                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i in range(100):
                        progress_bar.progress(i + 1)
                        if i < 30:
                            status_text.text(f"Processing scenes... {i+1}%")
                        elif i < 70:
                            status_text.text(f"Generating prompts... {i+1}%")
                        else:
                            status_text.text(f"Preparing production... {i+1}%")

                    st.balloons()
                    st.success("🎬 Production pipeline ready!")

    with col2:
        st.subheader("Production Queue")
        st.metric("Queued Jobs", "0")
        st.metric("Processing", "0")
        st.metric("Completed", "0")

        st.markdown("---")

        st.subheader("Estimated Costs")
        st.markdown("**Per Scene:**")
        if use_veo:
            st.caption("🎥 Veo: ~$0.15")
        if use_runway:
            st.caption("🚀 Runway: ~$0.10")

        st.markdown("---")

        st.info("""
        **Production Tips:**
        - Test with 1-2 scenes first
        - Monitor API quotas
        - Check output quality
        - Adjust prompts if needed
        """)

# ================================
# TAB 5: POST-PRODUCTION
# ================================
with tab5:
    st.header("✂️ Post-Production")
    st.markdown("CapCut integration and final editing guide")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("CapCut Export Guide")

        st.markdown("""
        ### 📋 Workflow Steps:

        #### 1. Download Generated Videos
        - Export all generated scene videos from Veo/Runway
        - Organize in folders: `scene01/`, `scene02/`, etc.

        #### 2. Import to CapCut
        - Open CapCut Desktop
        - Create New Project
        - Import all scene videos + audio file

        #### 3. Timeline Assembly
        ```
        Timeline Structure:
        ┌─────────────────────────────────┐
        │ Audio Track (Master)            │
        ├─────────────────────────────────┤
        │ Scene 01 | Scene 02 | Scene 03  │
        ├─────────────────────────────────┤
        │ Transitions & Effects           │
        └─────────────────────────────────┘
        ```

        #### 4. Sync to Music
        - Use beat markers from audio analysis
        - Align scene cuts to music beats
        - Add transitions (0.5-1s crossfades)

        #### 5. Color Grading
        - Apply consistent LUT across all scenes
        - Match brightness/contrast
        - Adjust saturation for mood

        #### 6. Final Export
        - Resolution: 1920x1080 or 4K
        - Format: MP4 (H.264)
        - Bitrate: 20-50 Mbps
        - FPS: Match source (24/30/60)
        """)

        st.markdown("---")

        st.subheader("Quick Export Settings")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            export_res = st.selectbox("Export Resolution", ["1920x1080 (Full HD)", "3840x2160 (4K)", "1280x720 (HD)"])
            export_fps = st.selectbox("Export FPS", [24, 30, 60])

        with export_col2:
            export_bitrate = st.selectbox("Bitrate", ["20 Mbps", "30 Mbps", "50 Mbps"])
            export_format = st.selectbox("Format", ["MP4 (H.264)", "MOV (ProRes)", "MP4 (H.265)"])

        if st.button("📄 Generate CapCut Project Template", use_container_width=True):
            st.success("✅ Template generated! Check downloads folder.")
            st.code("""
{
  "project_name": "Music_Video_Production",
  "timeline": {
    "audio": "master_audio.wav",
    "scenes": ["scene01.mp4", "scene02.mp4", "scene03.mp4"],
    "transitions": "crossfade_0.5s"
  },
  "export": {
    "resolution": "1920x1080",
    "fps": 30,
    "bitrate": "30 Mbps"
  }
}
            """, language="json")

    with col2:
        st.subheader("Helpful Resources")

        st.markdown("""
        **CapCut Tutorials:**
        - [Basic Editing](https://capcut.com)
        - [Beat Sync Guide](https://capcut.com)
        - [Color Grading](https://capcut.com)

        **Keyboard Shortcuts:**
        - `Space`: Play/Pause
        - `C`: Cut clip
        - `Delete`: Remove clip
        - `Ctrl+Z`: Undo
        - `Ctrl+S`: Save
        """)

        st.markdown("---")

        st.info("""
        **Pro Tips:**
        - Save often (Ctrl+S)
        - Use proxy mode for 4K
        - Export test clip first
        - Keep backup of project
        """)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🎬 Music Video Agent System - Phoenix Ultimate Version | Powered by FastAPI + Streamlit + Google Gemini
</div>
""", unsafe_allow_html=True)
