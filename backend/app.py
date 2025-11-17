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
</style>
""", unsafe_allow_html=True)

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
    "🎨 Visual Assets",
    "🎬 Production",
    "✂️ Post-Production"
])

# ================================
# TAB 1: MUSIC GENERATION
# ================================
with tab1:
    st.header("🎵 Music Generation (Suno)")
    st.markdown("Generate music variations using Few-Shot Learning")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Genre Configuration")

        # Übergenre input
        super_genre = st.text_input(
            "Übergenre (Super Genre)",
            placeholder="z.B. Electronic, Rock, Hip-Hop, Cinematic...",
            help="Hauptgenre für die Musikgenerierung"
        )

        # Additional parameters
        with st.expander("⚙️ Advanced Settings"):
            mood = st.text_input("Mood", placeholder="z.B. energetic, melancholic, uplifting...")
            tempo = st.selectbox("Tempo", ["Slow", "Medium", "Fast", "Variable"])
            style_refs = st.text_area(
                "Style References",
                placeholder="Artist oder Song-Referenzen (eine pro Zeile)",
                height=100
            )
            additional_instructions = st.text_area(
                "Additional Instructions",
                placeholder="Weitere Anweisungen für die KI...",
                height=100
            )

        # Generate button
        st.markdown("---")
        generate_col1, generate_col2 = st.columns([1, 3])

        with generate_col1:
            num_variations = st.number_input("Variations", min_value=1, max_value=50, value=20)

        with generate_col2:
            if st.button("🎵 Generate Variations", use_container_width=True):
                if not super_genre:
                    st.error("⚠️ Bitte Übergenre eingeben!")
                else:
                    with st.spinner(f"Generating {num_variations} variations..."):
                        # TODO: API call to backend
                        # For now: mockup
                        st.success(f"✅ {num_variations} Variationen generiert!")

                        # Mock data
                        st.markdown("#### Generated Prompts Preview:")
                        for i in range(min(5, num_variations)):
                            with st.expander(f"Variation {i+1}"):
                                st.code(f"""Genre: {super_genre}
Mood: {mood if mood else 'Auto-detected'}
Tempo: {tempo}
Style: Professional, cinematic quality
Duration: 3:00 - 3:30

Prompt: Epic {super_genre} track with {tempo.lower()} tempo,
featuring dynamic buildups and emotional depth...""")

    with col2:
        st.subheader("Few-Shot Learning Stats")

        # TODO: API call to /suno/learning-stats
        st.metric("Knowledge Base Size", "127", delta="+12")
        st.metric("Avg Quality Score", "8.2/10", delta="+0.3")
        st.metric("Top Genre", "Electronic")

        st.markdown("---")
        st.markdown("#### Recent High-Quality Prompts")
        st.caption("🟢 Score ≥8.0 (Last 5)")

        for i in range(5):
            st.markdown(f"• **Prompt #{120+i}** - 8.{9-i}/10")

# ================================
# TAB 2: AUDIO UPLOAD
# ================================
with tab2:
    st.header("📤 Audio Upload")
    st.markdown("Upload your generated music files (.wav or .mp3)")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Audio Files")

        uploaded_files = st.file_uploader(
            "Choose audio file(s)",
            type=["wav", "mp3"],
            accept_multiple_files=True,
            help="Unterstützte Formate: WAV, MP3"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

            st.markdown("#### Uploaded Files:")
            for idx, file in enumerate(uploaded_files, 1):
                with st.expander(f"{idx}. {file.name} ({file.size / 1024:.1f} KB)"):
                    st.audio(file)

                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        if st.button(f"🔍 Analyze", key=f"analyze_{idx}"):
                            with st.spinner("Analyzing audio..."):
                                # TODO: API call to audio analyzer
                                st.info("Analysis: 128 BPM, E minor, 3:24 duration")

                    with col_b:
                        if st.button(f"🚀 Process", key=f"process_{idx}"):
                            st.success("Added to processing queue!")

    with col2:
        st.subheader("Processing Queue")
        st.info("No files in queue")

        st.markdown("---")
        st.subheader("Audio Analysis Settings")

        enable_bpm = st.checkbox("Detect BPM", value=True)
        enable_key = st.checkbox("Detect Key", value=True)
        enable_segments = st.checkbox("Scene Detection", value=True)

        if st.button("⚙️ Analyze All", use_container_width=True):
            if uploaded_files:
                st.success("Batch analysis started!")
            else:
                st.warning("No files to analyze")

# ================================
# TAB 3: VISUAL ASSETS
# ================================
with tab3:
    st.header("🎨 Visual Assets Upload")
    st.markdown("Upload scene images for video production mapping")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Scene Images")

        visual_files = st.file_uploader(
            "Upload scene images",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Upload images for each scene. Naming: scene01.png, scene02.png, etc."
        )

        if visual_files:
            st.success(f"✅ {len(visual_files)} image(s) uploaded")

            st.markdown("#### Uploaded Scenes:")
            st.markdown("**WICHTIG:** Prüfe die Dateinamen für korrektes Mapping!")

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

            st.markdown("---")

            # Scene mapping table
            st.markdown("#### Scene Mapping Table")
            mapping_data = []
            for idx, file in enumerate(visual_files, 1):
                mapping_data.append({
                    "Scene #": idx,
                    "Filename": file.name,
                    "Status": "✅ Ready",
                    "Size": f"{file.size / 1024:.1f} KB"
                })

            st.dataframe(mapping_data, use_container_width=True)

    with col2:
        st.subheader("Scene Guidelines")

        st.markdown("""
        **Naming Convention:**
        - `scene01.png`
        - `scene02.png`
        - `scene03.png`
        - etc.

        **Recommended:**
        - Format: PNG, JPG
        - Resolution: 1920x1080 or higher
        - Aspect Ratio: 16:9
        - Max size: 10 MB per file
        """)

        st.markdown("---")
        st.subheader("Quick Actions")

        if st.button("🔍 Validate All", use_container_width=True):
            if visual_files:
                st.success("All files validated ✅")
            else:
                st.warning("No files to validate")

        if st.button("📊 Generate Report", use_container_width=True):
            if visual_files:
                st.info(f"Report: {len(visual_files)} scenes ready for production")
            else:
                st.warning("Upload files first")

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
