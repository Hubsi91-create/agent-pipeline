import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import os
import logging

# Logger für diesen Service
logger = logging.getLogger(__name__)

# (Projekt und Region des Benutzers sind korrekt)
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "music-agents-prod")
GOOGLE_REGION = os.getenv("GOOGLE_REGION", "global")

# Lade das Modell beim Start
model = None
try:
    if GOOGLE_PROJECT_ID != "dein-gcp-projekt-id":  # Sicherer Check
        vertexai.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_REGION)
        # (Modellname des Benutzers ist korrekt)
        model = GenerativeModel("gemini-2.5-pro")
        logger.info(f"Vertex AI (Gemini) erfolgreich initialisiert für Projekt {GOOGLE_PROJECT_ID}.")
    else:
        logger.warning("Vertex AI (Gemini) NICHT initialisiert. GOOGLE_PROJECT_ID wurde nicht gesetzt.")
except Exception as e:
    logger.error(f"SCHWERER FEHLER: Konnte Vertex AI nicht initialisieren. Fehler: {e}")

def call_gemini(prompt_text: str) -> str:
    """
    Ruft das Gemini-Modell mit einem gegebenen Text-Prompt auf.
    Verwendet generate_content mit stream=True, da gemini-2.5-pro dies erfordert.
    """
    if model is None:
        logger.error("Gemini-Aufruf fehlgeschlagen: Modell ist nicht initialisiert (GOOGLE_PROJECT_ID prüfen!).")
        return "Fehler: Vertex AI (Gemini) ist nicht korrekt initialisiert."

    try:
        # 1. Erstelle das offizielle Konfigurations-OBJEKT
        #    (Das behebt den alten 'TypeError')
        config = GenerationConfig(
            temperature=0.8,
            top_p=0.95,
            max_output_tokens=8192
        )

        # 2. Sende den Prompt an das Modell mit der KORREKTEN FUNKTION
        #    UND den KORREKTEN PARAMETERN
        response_stream = model.generate_content(
            [Part.from_text(prompt_text)],
            generation_config=config,  # <-- FIX 1 (Das Objekt)
            stream=True                # <-- FIX 2 (Der Streaming-Parameter)
        )

        # 3. Da es ein Stream ist, müssen wir die Teile zusammensetzen
        full_text = ""
        for chunk in response_stream:
            try:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    full_text += chunk.candidates[0].content.parts[0].text
            except (AttributeError, IndexError, ValueError):
                pass

        if full_text:
            return full_text
        else:
            logger.warning("Gemini-Stream war leer oder im falschen Format.")
            return "Fehler: Konnte keine valide Antwort vom Modell erhalten (Stream war leer)."

    except Exception as e:
        logger.error(f"Fehler bei Gemini-Aufruf (generate_content mit stream=True): {e}")
        error_message = str(e)
        if "400" in error_message:
             return f"Fehler bei der Textgenerierung: 400 Bad Request. (Details: {error_message})"
        return f"Fehler bei der Textgenerierung: {error_message}"

def generate_song_lyrics(theme: str, genre: str, mood: str, target_words: int, bpm: int, vocal_style: str) -> str:
    """
    Erstellt einen spezialisierten Prompt und ruft call_gemini auf, um Songtexte zu generieren.
    """
    logger.info(f"Generiere Songtext für Thema: {theme}, Genre: {genre}, Wörter: {target_words}")

    lyric_generation_prompt = f"""
Schreibe einen kompletten Songtext im Stil von '{genre}' zum Thema '{theme}'.
Der Songtext muss exakt {target_words} Wörter lang sein.
Die Stimmung ist: {mood}.
Der Vocal Style ist: {vocal_style}.
Der Song hat {bpm} BPM.
Strukturiere den Text mit Tags wie [Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Final Chorus], [Outro].
Stelle sicher, dass die Wortanzahl genau eingehalten wird.
"""

    return call_gemini(lyric_generation_prompt)

def generate_video_concept(theme: str, genre: str, mood: str, lyrics: str) -> str:
    """
    Erstellt einen spezialisierten Prompt für ein Video-Konzept.
    """
    logger.info(f"Generiere Video-Konzept für Thema: {theme}")

    concept_prompt = f"""
Basierend auf dem folgenden Songtext (Thema: {theme}, Genre: {genre}, Stimmung: {mood}),
erstelle ein detailliertes Video-Konzept.

Songtext:
{lyrics}

Video-Konzept:
"""

    return call_gemini(concept_prompt)
