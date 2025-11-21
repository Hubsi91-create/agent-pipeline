"""
PROJECT PHOENIX - Native Desktop Application
Modern Desktop UI with Direct Service Integration
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

import customtkinter as ctk
import asyncio
import threading
import json
import logging
from typing import Optional, List, Dict
from datetime import datetime
from queue import Queue

# Direct imports from backend services
from app.agents.agent_1_project_manager.service import agent1_service
from app.agents.agent_3_audio_analyzer.service import agent3_service
from app.agents.agent_4_scene_breakdown.service import agent4_service
from app.agents.agent_5_style_anchors.service import agent5_service
from app.agents.agent_6_veo_prompter.service import agent6_service
from app.agents.agent_7_runway_prompter.service import agent7_service
from app.agents.agent_8_refiner.service import agent8_service
from app.agents.agent_9_capcut.service import agent9_service
from app.agents.agent_10_youtube.service import agent10_service
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger

logger = setup_logger("DesktopApp")


# ================================
# CUSTOM LOGGING HANDLER FOR GUI
# ================================
class GuiHandler(logging.Handler):
    """Custom logging handler that writes to the GUI console"""

    def __init__(self, app):
        super().__init__()
        self.app = app

        # Color mapping for log levels
        self.level_colors = {
            "DEBUG": "#00f2ff",      # Cyan
            "INFO": "#00ff88",       # Green
            "WARNING": "#ffaa00",    # Orange
            "ERROR": "#ff0055",      # Red/Magenta
            "CRITICAL": "#ff0055",   # Red/Magenta
        }

    def emit(self, record):
        """Emit a log record to the app's log message handler"""
        try:
            msg = self.format(record)
            level_name = record.levelname
            # Call app's log_message method (thread-safe via queue)
            self.app.log_message(msg, level_name)
        except Exception:
            self.handleError(record)

# ================================
# DEEP SPACE THEME COLORS
# ================================
COLORS = {
    "bg_dark": "#050505",
    "bg_glass": "#0a0a0a",
    "accent_cyan": "#00f2ff",
    "accent_magenta": "#ff0055",
    "text_primary": "#ffffff",
    "text_secondary": "#aaaaaa",
    "border": "#1a1a1a",
    "success": "#00ff88",
    "error": "#ff0055",
}


class PhoenixDesktopApp:
    """Main Desktop Application Class"""

    def __init__(self):
        """Initialize the application"""
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("PROJECT PHOENIX")
        self.root.geometry("1400x900")
        self.root.configure(fg_color=COLORS["bg_dark"])

        # Session state (like Streamlit st.session_state)
        self.state = {
            "viral_trends": [],
            "selected_supergenre": None,
            "genre_variations": [],
            "selected_variations": [],
            "audio_scenes": [],
            "available_styles": [],
            "video_prompts": None,
            "capcut_guide": None,
            "youtube_metadata": None,
        }

        # Logging setup - Initialize queue immediately
        self.log_queue = Queue()
        self.console_widget = None
        self.gui_handler = None

        # Genre checkboxes for selection
        self.genre_checkboxes = []

        # Async event loop for non-blocking operations
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()

        # Setup logging BEFORE building UI
        self._setup_logging()

        # Build UI
        self._build_ui()

        # Start processing log queue
        self._process_log_queue()

        logger.info("🚀 PROJECT PHOENIX - Desktop App Started Successfully")

    def _run_async_loop(self):
        """Run async event loop in background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _build_ui(self):
        """Build the main UI structure"""
        # Main container with grid layout
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.root.grid_columnconfigure(1, weight=1)  # Main content (expandable)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._build_sidebar()

        # Main content area
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header
        self._build_header()

        # Content container (will be filled by navigation)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Load initial view
        self.show_trends_view()

    def _build_sidebar(self):
        """Build navigation sidebar"""
        sidebar = ctk.CTkFrame(self.root, width=280, fg_color=COLORS["bg_glass"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Logo section
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=30, padx=20)

        ctk.CTkLabel(
            logo_frame,
            text="🌌 PROJECT PHOENIX",
            font=ctk.CTkFont(family="Orbitron", size=20, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="ADVANCED AGENTIC PIPELINE",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"],
        ).pack()

        # Navigation buttons
        nav_buttons = [
            ("📈 Viral Trends", self.show_trends_view),
            ("🎵 Genre Lab", self.show_genre_lab_view),
            ("🎧 Audio Analysis", self.show_audio_view),
            ("🎨 Visual Core", self.show_visual_view),
            ("🎬 Production", self.show_production_view),
            ("✂️ Post-Production", self.show_postpro_view),
            ("🔧 System Logs", self.show_debugger_view),
        ]

        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color=COLORS["border"],
                border_width=1,
                border_color=COLORS["border"],
                text_color=COLORS["text_secondary"],
                anchor="w",
            )
            btn.pack(pady=5, padx=20, fill="x")

    def _build_header(self):
        """Build header with status indicator"""
        header = ctk.CTkFrame(self.main_frame, height=80, fg_color=COLORS["bg_glass"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            header,
            text="MISSION CONTROL",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w", padx=30, pady=20)

        # Status indicator
        status_frame = ctk.CTkFrame(header, fg_color=COLORS["border"], corner_radius=20)
        status_frame.grid(row=0, column=1, sticky="e", padx=30, pady=20)

        ctk.CTkLabel(
            status_frame,
            text="● SYSTEM ONLINE",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["success"],
        ).pack(padx=15, pady=8)

    def clear_content(self):
        """Clear current content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ================================
    # VIEW 1: VIRAL TRENDS
    # ================================
    def show_trends_view(self):
        """Display viral trends scanning interface"""
        self.clear_content()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="📈 VIRAL TREND SCANNER",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)

        # Button frame
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")

        # Scan button
        ctk.CTkButton(
            button_frame,
            text="🔄 SCAN GLOBAL NETWORKS",
            command=self.scan_trends,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_magenta"],
            text_color=COLORS["bg_dark"],
        ).pack(side="left", padx=5)

        # Copy button
        ctk.CTkButton(
            button_frame,
            text="📋 Copy Trends",
            command=self.copy_trends_to_clipboard,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["border"],
            hover_color=COLORS["accent_cyan"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=5)

        # Copy status label
        self.trends_copy_status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["success"],
        )
        self.trends_copy_status_label.pack(side="left", padx=15)

        # Trends display area (using Textbox for copyability)
        self.trends_textbox = ctk.CTkTextbox(
            self.content_frame,
            fg_color=COLORS["bg_glass"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            activate_scrollbars=True,
        )
        self.trends_textbox.pack(fill="both", expand=True, pady=20)

        # Load existing trends if available
        if self.state["viral_trends"]:
            self._display_trends()
        else:
            # Load initial trends
            self.run_async(self._load_initial_trends())

    async def _load_initial_trends(self):
        """Load initial trends from service"""
        try:
            trends = await agent1_service.get_current_viral_trends()
            self.state["viral_trends"] = trends
            self.root.after(0, self._display_trends)
        except Exception as e:
            logger.error(f"Failed to load trends: {e}")

    def _display_trends(self):
        """Display trends in the UI as formatted text"""
        if not hasattr(self, 'trends_textbox'):
            return  # Textbox not created yet

        # Clear existing content
        self.trends_textbox.delete("0.0", "end")

        # Build formatted trend text
        trend_text = "=" * 80 + "\n"
        trend_text += "🌍 GLOBAL VIRAL MUSIC TRENDS\n"
        trend_text += "=" * 80 + "\n\n"

        for i, trend in enumerate(self.state["viral_trends"], 1):
            genre = trend.get("genre", "Unknown")
            platform = trend.get("platform", "Mixed")
            score = trend.get("trend_score", "🔥")
            description = trend.get("description", "")

            trend_text += f"{i}. {genre}\n"
            trend_text += f"   Platform: {platform}\n"
            trend_text += f"   Trend Score: {score}\n"
            if description:
                trend_text += f"   Description: {description}\n"
            trend_text += "\n"

        trend_text += "=" * 80 + "\n"
        trend_text += f"Total Trends: {len(self.state['viral_trends'])}\n"

        # Insert text
        self.trends_textbox.insert("0.0", trend_text)

    def copy_trends_to_clipboard(self):
        """Copy all trends to clipboard"""
        try:
            # Get all text from trends textbox
            if hasattr(self, 'trends_textbox'):
                trend_text = self.trends_textbox.get("0.0", "end")

                # Copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(trend_text)
                self.root.update()

                # Show confirmation
                self.trends_copy_status_label.configure(text="✓ Copied to clipboard!")
                # Clear confirmation after 2 seconds
                self.root.after(2000, lambda: self.trends_copy_status_label.configure(text=""))

                logger.info("Trends copied to clipboard")
            else:
                logger.warning("Trends textbox not available")

        except Exception as e:
            logger.error(f"Failed to copy trends: {e}")
            self.trends_copy_status_label.configure(text="✗ Copy failed", text_color=COLORS["error"])

    def scan_trends(self):
        """Scan for new viral trends"""
        self.run_async(self._scan_trends_async())

    async def _scan_trends_async(self):
        """Async trend scanning with proper UI updates"""
        try:
            # Update UI to show scanning
            self.root.after(0, lambda: self._show_status("🔄 Scanning global networks..."))
            logger.info("🌍 Starting viral trend scan...")

            # Call service
            result = await agent1_service.update_viral_trends()

            if result.get("status") == "success":
                trends = result.get("trends", [])
                self.state["viral_trends"] = trends

                logger.info(f"✅ Trend scan successful: {len(trends)} trends found")

                # Update UI on main thread
                def update_ui():
                    self._display_trends()
                    self._show_status(f"✓ Found {len(trends)} trends")

                self.root.after(0, update_ui)
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"❌ Trend scan failed: {error_msg}")
                self.root.after(0, lambda: self._show_status(f"✗ Scan failed: {error_msg}"))

        except Exception as e:
            logger.error(f"❌ Trend scan error: {e}")
            self.root.after(0, lambda: self._show_status(f"✗ Error: {str(e)}"))

    # ================================
    # VIEW 2: GENRE LAB
    # ================================
    def show_genre_lab_view(self):
        """Display genre exploration interface"""
        self.clear_content()

        ctk.CTkLabel(
            self.content_frame,
            text="🎵 GENRE LABORATORY",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)

        # Genre input
        input_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        input_frame.pack(pady=10, fill="x")

        self.genre_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter genre (e.g., Electronic, Hip-Hop, Reggaeton...)",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.genre_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            input_frame,
            text="Generate Variations",
            command=self.generate_variations,
            height=40,
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_magenta"],
            text_color=COLORS["bg_dark"],
        ).pack(side="right")

        # Variations display
        self.variations_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_glass"],
            corner_radius=10,
        )
        self.variations_frame.pack(fill="both", expand=True, pady=20)

    def generate_variations(self):
        """Generate genre variations"""
        genre = self.genre_entry.get().strip()
        if not genre:
            self._show_status("Please enter a genre")
            return

        self.run_async(self._generate_variations_async(genre))

    async def _generate_variations_async(self, genre: str):
        """Async variation generation"""
        try:
            self.root.after(0, lambda: self._show_status(f"Synthesizing {genre} variations..."))

            variations = await agent1_service.generate_genre_variations(genre, num_variations=20)
            self.state["genre_variations"] = variations
            self.state["selected_supergenre"] = genre

            self.root.after(0, self._display_variations)
            self.root.after(0, lambda: self._show_status(f"✓ Generated {len(variations)} variations"))

        except Exception as e:
            logger.error(f"Variation generation error: {e}")
            self.root.after(0, lambda: self._show_status(f"✗ Error: {str(e)}"))

    def _display_variations(self):
        """Display genre variations with checkboxes for selection"""
        for widget in self.variations_frame.winfo_children():
            widget.destroy()

        # Clear previous checkboxes
        self.genre_checkboxes = []

        # Instructions
        ctk.CTkLabel(
            self.variations_frame,
            text="✓ Select subgenres to explore (click checkboxes):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent_cyan"],
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(5, 10))

        for i, variation in enumerate(self.state["genre_variations"]):
            var_card = ctk.CTkFrame(self.variations_frame, fg_color=COLORS["border"], corner_radius=8)
            var_card.pack(fill="x", pady=5, padx=10)

            # Checkbox
            checkbox_var = ctk.IntVar(value=0)
            checkbox = ctk.CTkCheckBox(
                var_card,
                text="",
                variable=checkbox_var,
                width=30,
                fg_color=COLORS["accent_cyan"],
                hover_color=COLORS["accent_magenta"],
            )
            checkbox.pack(side="left", padx=10)

            # Store checkbox variable for later retrieval
            self.genre_checkboxes.append({
                "variation": variation,
                "var": checkbox_var
            })

            # Content container
            content_frame = ctk.CTkFrame(var_card, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

            ctk.CTkLabel(
                content_frame,
                text=variation.get("subgenre", "Unknown"),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                content_frame,
                text=variation.get("description", ""),
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"],
                anchor="w",
                wraplength=600,
            ).pack(anchor="w", pady=(2, 0))

        # Action buttons
        action_frame = ctk.CTkFrame(self.variations_frame, fg_color="transparent")
        action_frame.pack(pady=15, fill="x", padx=10)

        ctk.CTkButton(
            action_frame,
            text="✓ Confirm Selection",
            command=self.confirm_genre_selection,
            height=40,
            fg_color=COLORS["success"],
            hover_color=COLORS["accent_cyan"],
            text_color=COLORS["bg_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame,
            text="Select All",
            command=self.select_all_genres,
            height=40,
            fg_color=COLORS["border"],
            hover_color=COLORS["accent_magenta"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=5)

    def select_all_genres(self):
        """Select all genre checkboxes"""
        for checkbox_data in self.genre_checkboxes:
            checkbox_data["var"].set(1)
        logger.info("Selected all genre variations")

    def confirm_genre_selection(self):
        """Confirm selected genres and save to state"""
        selected = []
        for checkbox_data in self.genre_checkboxes:
            if checkbox_data["var"].get() == 1:
                selected.append(checkbox_data["variation"])

        self.state["selected_variations"] = selected
        logger.info(f"✓ Confirmed {len(selected)} genre selections: {[v['subgenre'] for v in selected]}")
        self._show_status(f"✓ Selected {len(selected)} subgenres")

    # ================================
    # VIEW 3: AUDIO ANALYSIS
    # ================================
    def show_audio_view(self):
        """Display audio analysis interface"""
        self.clear_content()

        ctk.CTkLabel(
            self.content_frame,
            text="🎧 AUDIO ANALYZER",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)

        ctk.CTkLabel(
            self.content_frame,
            text="Upload audio file and analyze waveform structure",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=10)

        # File selection button
        ctk.CTkButton(
            self.content_frame,
            text="📁 Select Audio File",
            command=self.select_audio_file,
            height=45,
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_magenta"],
            text_color=COLORS["bg_dark"],
        ).pack(pady=20)

        # Selected file label
        self.audio_file_label = ctk.CTkLabel(
            self.content_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        )
        self.audio_file_label.pack(pady=5)

        # Analyze button (initially disabled)
        self.analyze_button = ctk.CTkButton(
            self.content_frame,
            text="▶️ Analyze Audio",
            command=self.analyze_audio,
            height=45,
            fg_color=COLORS["success"],
            hover_color=COLORS["accent_cyan"],
            text_color=COLORS["bg_dark"],
            state="disabled",
        )
        self.analyze_button.pack(pady=10)

        # Results area
        self.audio_results_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_glass"],
            corner_radius=10,
        )
        self.audio_results_frame.pack(fill="both", expand=True, pady=20)

    def select_audio_file(self):
        """Open file dialog to select audio file"""
        from tkinter import filedialog
        import os

        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac"), ("All Files", "*.*")]
        )

        if file_path:
            # Store selected file path
            self.state["selected_audio_file"] = file_path

            # Update label to show selected file
            filename = os.path.basename(file_path)
            self.audio_file_label.configure(
                text=f"✓ Selected: {filename}",
                text_color=COLORS["success"]
            )

            # Enable analyze button
            self.analyze_button.configure(state="normal")

            logger.info(f"📁 Audio file selected: {file_path}")
            self._show_status(f"✓ File selected: {filename}")

    def analyze_audio(self):
        """Analyze the selected audio file"""
        file_path = self.state.get("selected_audio_file")
        if not file_path:
            self._show_status("✗ No file selected")
            return

        logger.info(f"🎵 Starting audio analysis: {file_path}")
        self._show_status("Analyzing audio file...")
        self.run_async(self._analyze_audio_async(file_path))

    async def _analyze_audio_async(self, file_path: str):
        """Async audio analysis"""
        try:
            # Call Agent 3 for audio analysis
            result = await agent3_service.analyze_audio(file_path)

            # Display results in UI
            self.root.after(0, lambda: self._display_audio_results(result))
            self.root.after(0, lambda: self._show_status("✓ Audio analysis completed"))

        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            self.root.after(0, lambda: self._show_status(f"✗ Error: {str(e)}"))
            self.root.after(0, lambda: self._display_audio_error(str(e)))

    def _display_audio_results(self, result):
        """Display audio analysis results"""
        for widget in self.audio_results_frame.winfo_children():
            widget.destroy()

        # Title
        ctk.CTkLabel(
            self.audio_results_frame,
            text="📊 ANALYSIS RESULTS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=10)

        # Display scenes if available
        scenes = result.get("scenes", [])
        if scenes:
            for i, scene in enumerate(scenes):
                scene_card = ctk.CTkFrame(self.audio_results_frame, fg_color=COLORS["border"], corner_radius=8)
                scene_card.pack(fill="x", pady=5, padx=10)

                ctk.CTkLabel(
                    scene_card,
                    text=f"Scene {i+1}: {scene.get('timestamp', '')}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text_primary"],
                ).pack(anchor="w", padx=15, pady=5)

                ctk.CTkLabel(
                    scene_card,
                    text=scene.get("description", ""),
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                ).pack(anchor="w", padx=15, pady=(0, 10))

    def _display_audio_error(self, error_msg: str):
        """Display error message in audio results frame"""
        for widget in self.audio_results_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.audio_results_frame,
            text="❌ ANALYSIS FAILED",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["error"],
        ).pack(pady=10)

        ctk.CTkLabel(
            self.audio_results_frame,
            text=error_msg,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=600,
        ).pack(pady=5)

    # ================================
    # PLACEHOLDER VIEWS (For remaining tabs)
    # ================================
    def show_visual_view(self):
        """Display visual style interface"""
        self.clear_content()
        ctk.CTkLabel(
            self.content_frame,
            text="🎨 VISUAL CORE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)
        ctk.CTkLabel(
            self.content_frame,
            text="Style presets and image-based style learning coming soon...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=10)

    def show_production_view(self):
        """Display production interface"""
        self.clear_content()
        ctk.CTkLabel(
            self.content_frame,
            text="🎬 PRODUCTION SUITE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)
        ctk.CTkLabel(
            self.content_frame,
            text="Video prompt generation coming soon...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=10)

    def show_postpro_view(self):
        """Display post-production interface"""
        self.clear_content()
        ctk.CTkLabel(
            self.content_frame,
            text="✂️ POST-PRODUCTION",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)
        ctk.CTkLabel(
            self.content_frame,
            text="CapCut guides and YouTube metadata coming soon...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=10)

    # ================================
    # VIEW 7: DEBUGGER / SYSTEM LOGS
    # ================================
    def show_debugger_view(self):
        """Display live system console with logs and agent testing"""
        self.clear_content()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="🔧 DEBUGGER & SYSTEM CONSOLE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent_cyan"],
        ).pack(pady=20)

        # Control buttons
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")

        ctk.CTkButton(
            button_frame,
            text="📋 Copy All Logs",
            command=self.copy_logs_to_clipboard,
            height=35,
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_magenta"],
            text_color=COLORS["bg_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Clear Console",
            command=self.clear_console,
            height=35,
            fg_color=COLORS["border"],
            hover_color=COLORS["error"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=5)

        # Status label for copy confirmation
        self.copy_status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["success"],
        )
        self.copy_status_label.pack(side="left", padx=15)

        # Create console widget if it doesn't exist
        if not self.console_widget:
            # Console textbox (scrollable)
            self.console_widget = ctk.CTkTextbox(
                self.content_frame,
                fg_color="#000000",
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Consolas", size=11),
                wrap="word",
                activate_scrollbars=True,
            )

            # Add welcome message
            self._append_to_console("=== PROJECT PHOENIX SYSTEM CONSOLE ===", "INFO")
            self._append_to_console("All agent operations and system events will appear here.", "INFO")
            self._append_to_console("=" * 50, "INFO")

        # Pack the console (it may have been unpacked from previous view)
        self.console_widget.pack(fill="both", expand=True, pady=10)

    def copy_logs_to_clipboard(self):
        """Copy all console logs to clipboard"""
        try:
            # Get all text from console
            log_text = self.console_widget.get("0.0", "end")

            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(log_text)
            self.root.update()  # Required for clipboard to work

            # Show confirmation
            self.copy_status_label.configure(text="✓ Copied to clipboard!")
            # Clear confirmation after 2 seconds
            self.root.after(2000, lambda: self.copy_status_label.configure(text=""))

            logger.info("Logs copied to clipboard")

        except Exception as e:
            logger.error(f"Failed to copy logs: {e}")
            self.copy_status_label.configure(text="✗ Copy failed", text_color=COLORS["error"])

    def clear_console(self):
        """Clear all console logs"""
        if not self.console_widget:
            return

        try:
            self.console_widget.delete("0.0", "end")

            # Add reset message
            self._append_to_console("=== CONSOLE CLEARED ===\n", "INFO")

            logger.info("Console cleared")

        except Exception as e:
            logger.error(f"Failed to clear console: {e}")

    def _append_to_console(self, message: str, level: str = "INFO"):
        """Append a message to the console with color coding"""
        if not self.console_widget:
            return  # Console not created yet

        try:
            # Insert text (CTkTextbox is always editable by default)
            self.console_widget.insert("end", message + "\n")

            # Auto-scroll to bottom
            self.console_widget.see("end")

        except Exception as e:
            # Silently fail if console not ready
            pass

    def log_message(self, message: str, level: str = "INFO"):
        """
        Thread-safe method to log a message
        Puts message in queue for GUI thread to process
        """
        self.log_queue.put((message, level))

    def _setup_logging(self):
        """Setup logging handler to capture all logs"""
        try:
            # Create custom handler that uses log_message
            self.gui_handler = GuiHandler(self)

            # Set format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            self.gui_handler.setFormatter(formatter)

            # Add handler to root logger to capture ALL logs
            root_logger = logging.getLogger()
            root_logger.addHandler(self.gui_handler)
            root_logger.setLevel(logging.DEBUG)

            logger.info("✅ Live console logging enabled")

        except Exception as e:
            print(f"❌ Failed to setup logging: {e}")

    def _process_log_queue(self):
        """Process log queue and update console (thread-safe)"""
        try:
            # Process all pending log messages
            while not self.log_queue.empty():
                message, level = self.log_queue.get_nowait()
                if self.console_widget:
                    self._append_to_console(message, level)

        except Exception as e:
            # Silently continue if queue is empty or console not ready
            pass
        finally:
            # Schedule next check (every 100ms)
            self.root.after(100, self._process_log_queue)

    # ================================
    # UTILITY METHODS
    # ================================
    def _show_status(self, message: str):
        """Display status message in header"""
        # TODO: Implement status bar or notification system
        logger.info(f"Status: {message}")

    def run_async(self, coro):
        """Run async coroutine in background thread"""
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def run(self):
        """Start the application"""
        logger.info("🚀 Starting Desktop App UI...")
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = PhoenixDesktopApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
