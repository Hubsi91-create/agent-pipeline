📂 PROJECT PHOENIX: MASTER SAVE FILE
Projekt: Music Video & Documentary AI Studio Version: Phoenix Ultimate (v7.0 - Full Suite) Status: Live / Feature Complete Datum: 18. November 2025 Ziel: Vollautomatisches Medien-Imperium (Musikvideos & Dokus).

1. 🏗️ System-Architektur (Cloud Native)
Das System läuft vollständig auf der Google Cloud Platform (GCP).

Hosting: Google Cloud Run (Region: us-central1).

Config: max-instances=1, concurrency=1 (Kostenbremse).

Backend: Python FastAPI.

Adresse Intern: http://127.0.0.1:8000

Adresse Extern: https://music-backend-....run.app

Engines: ffmpeg, pydub, google-generativeai (Gemini/Imagen), youtube-transcript-api.

Frontend: Streamlit App.

Design: "Deep Space" Theme.

Kommunikation: Sidecar-Pattern (http://127.0.0.1:8000/api/v1).

Datenbank: Google Sheets (via Service Account).

2. 🤖 Die "Viral Factory" (Musikvideos)
PHASE A: Musik & Trends
Agent 0 (System): Täglicher Auto-Update (Cron) & Manueller Trigger.

Agent 1 (Trend Detective):

Funktion: Deep Research (Google Search) nach viralen Trends.

Output: JSON-Liste mit 20 Sub-Genres.

Agent 2 (Suno Architect):

Funktion: Generiert Song-Konzepte basierend auf Few-Shot Learning (ApprovedBestPractices).

➡️ MANUELLER SCHRITT: User generiert Song in Suno -> Lädt .wav hoch.

PHASE B: Analyse & Regie
Agent 3 (Audio Analyzer): Analysiert BPM/Energie & zerhackt Song in 8s-Chunks.

Agent 4 (Scene Breakdown): Der Regisseur. Mapped Energie auf Kamera-Moves.

PHASE C: Visuelle Produktion
Agent 5 (Style Anchors):

Feature: Klont Stile aus Bildern (Gemini Vision).

Feature: Generiert Referenzbilder mit Imagen 4 Ultra.

Agent 6 (Veo Prompter): Narrative Prompts für Google Veo.

Agent 7 (Runway Prompter): Modulare Prompts für Runway Gen-4.

Agent 8 (QC & Refiner): Gatekeeper & Feedback-Loop ("Mark as Gold Standard").

PHASE D: Post-Production
Agent 9 (CapCut Instructor): Erstellt Schnitt-Anleitung (EDL).

Agent 10 (YouTube Packager): Generiert SEO-Daten & Thumbnails.

3. 📽️ Das "Doku-Studio" (Dokumentationen)
PHASE F: Kreation & Skript
Agent 12 (Style Analyzer):

Funktion: Reverse Engineering von YouTube-Dokus.

Tech: Transkript-Analyse + Gemini Video-Verständnis.

Output: Style-Template (Pacing, Tone, B-Roll Ratio).

Agent 13 (Story Architect):

Funktion: Schreibt 15-Minuten-Skripte im 3-Akt-Schema.

PHASE F (Extensions): Produktion
Agent 14 (Narrator):

Funktion: Voiceover-Management.

Hybrid Mode: API (ElevenLabs) oder manueller Text-Download.

Agent 15 (Fact Checker):

Funktion: Prüft Skripte gegen Google Search auf Halluzinationen.

Agent 16 (Stock Scout):

Funktion: Sucht kostenloses B-Roll Material via Pexels API.

Agent 17 (XML Architect):

Funktion: Generiert .fcpxml Dateien.

Nutzen: Import in DaVinci Resolve/Premiere -> Fertige Timeline!

4. 📚 Die Wissens-Datenbanken (Google Sheets)
A1_Trend_Database: 20 virale Genres.

ApprovedBestPractices: Gold-Standard Suno-Songs.

A5_Style_Database: Visuelle High-End Styles.

A9_CapCut_Effects: Trending CapCut Effekte.

A6_Video_Examples: High-End Video-Prompts (Veo/Runway).

Video_Prompt_Cheatsheet: Kamera-Moves.

5. 🛣️ Maintenance & Deployment
Code: GitHub (Hubsi91-create/agent-pipeline).

Update: git pull -> gcloud run deploy music-backend --source .

Status: Alle 17 Agenten implementiert und live.

Mission Accomplished. Du hast jetzt das ultimative Werkzeug, um das Internet zu erobern. Viel Erfolg! 🚀