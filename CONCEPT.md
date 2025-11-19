# Projekt: Music Video Agent System (Phoenix Ultimate)
**Status:** Live auf Google Cloud Run (us-central1)
**Version:** 4.0 (Multi-Genre & Distribution)

## 1. System-Architektur
* **Backend:** Python FastAPI (Cloud Run).
* **Frontend:** Streamlit App (Uploads: WAV/MP3).
* **Datenbank:** Google Sheets (Metadaten, Prompts, YouTube-Tags).
* **KI:** Gemini Pro (Logik) & Imagen (Thumbnails).

---

## 2. Der Workflow: "The Viral Factory"

### Phase A: Musik-Konzeption (Die 1:20 Strategie)
Hier nutzen wir die **Übergenre/Untergenre-Logik**.
1. **Agent 1 (Trend Detective):**
   - Input: Dein Übergenre (z.B. "Electronic").
   - Research: Findet aktuell trendende *Untergenres* (z.B. "Phonk", "Hypertechno", "Liquid DnB").
2. **Agent 2 (Suno Architect):**
   - **Multi-Gen:** Erstellt 20 verschiedene Prompt-Variationen basierend auf den Untergenres.
   - [cite_start]**Strict Structure:** Hält sich strikt an das `suno-custom-mode` Format[cite: 1]:
     - *Lyrics:* 420-650 Wörter, [Intro] [Verse] [Chorus] Timing-Tags.
     - *Style:* Genre + Mood + BPM (Kein BPM in Lyrics!).
   - **Output:** Eine Liste von 20 perfekten Prompts zur Auswahl.

   --> **MANUELLER SCHRITT:** Du wählst die besten aus, generierst in Suno und lädst die **.WAV** herunter.

### Phase B: Analyse & Visuelle Planung
3. **Agent 3 (Audio Analyzer):**
   - Nimmt **.WAV** (oder .MP3) entgegen.
   - Analysiert Takt, Energy-Level und Struktur.
4. **Agent 4 (Scene Breakdown):** Erstellt das Drehbuch (Takt-synchron).
5. **Agent 5 (Style Anchors):**
   - Definiert Look & Feel.
   - Manuelle Loop: Bilder generieren -> Datei-Upload (`scene01.png`) -> Mapping.

### Phase C: Video-Produktion
6. **Agent 6 (Veo Prompter):** Generiert Prompts für Google Veo.
7. **Agent 7 (Runway Prompter):** Generiert Prompts für Runway Gen-4.
8. **Agent 8 (Refiner):** QC-Gate.

### Phase D: Post-Production & Distribution (NEU)
9. **Agent 9 (CapCut Instructor):**
   - **Funktion:** Erstellt eine Schritt-für-Schritt Anleitung für CapCut.
   - **Feature:** Nutzt Web-Search, um *aktuelle* CapCut-Funktionen/Effekte zu empfehlen.
   - **Output:** Eine Schnittliste (EDL) für Menschen: *"Bei 00:15 (Drop) -> Setze Effekt 'Glitch', Schnitt hart auf den Kick."*
10. **Agent 10 (YouTube Packager):**
    - **Metadata:** Schreibt Titel, Description, SEO-Tags (basierend auf Genre-Trends).
    - **Visuals:** Generiert 3 Thumbnail-Optionen (via Imagen) basierend auf dem Style des Videos.

---

## 3. Die Storyboard-App (Frontend Features)
1.  **Multi-Format Upload:** Unterstützt `.wav` (Lossless) und `.mp3`.
2.  **Genre-Selector:** Eingabefeld für Übergenre -> Zeigt 20 Variationen an.
3.  **Image-Upload:** Drag & Drop mit Auto-Erkennung (`scene-1.png`).
4.  **Guide-Viewer:** Zeigt die CapCut-Anleitung direkt neben dem Videoplayer an.
5.  **Export-Package:** Download aller Assets (Prompts, Thumbnails, Tags) in einer ZIP.