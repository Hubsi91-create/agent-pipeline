import os
import json
import subprocess
import logging
import base64
import shutil
import asyncio
from typing import Optional, Dict, Any, List

# Configure logger
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Hybrid Service for interacting with Gemini.
    
    Strategies:
    1. Text Generation: Uses 'gemini' CLI (Node.js wrapper) to leverage the user's 
       Google AI Ultra Subscription (via 'gemini login').
    2. Image Analysis: Uses direct API calls via 'curl' (requires GEMINI_API_KEY) 
       because the CLI tool currently has limited support for image input flags.
    """

    def __init__(self):
        # Check for CLI availability
        self.cli_available = shutil.which("gemini") is not None
        
        # Check for API Key (fallback/images)
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.cli_available:
            logger.info("✅ Gemini Service: CLI found. Text generation will use User Subscription.")
        else:
            logger.warning("⚠️ Gemini Service: 'gemini' CLI not found. Text generation will fail! Install with: npm install -g @google/gemini-cli")

        if not self.api_key:
            logger.warning("⚠️ Gemini Service: GEMINI_API_KEY not found. Image analysis will fail.")

    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gemini-2.5-pro", 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_mime_type: Optional[str] = None,
        use_search: bool = False
    ) -> Optional[str]:
        """
        Generates text using the Gemini CLI (Node.js).
        
        Args:
            prompt: The input text prompt.
            model_name: The model to use (default: gemini-2.5-pro).
            temperature: (Ignored by CLI currently, model default used).
            max_tokens: (Ignored by CLI currently).
            response_mime_type: If "application/json", appends instruction to prompt.
            use_search: (Ignored by CLI currently).

        Returns:
            The generated text or None if failed.
        """
        if not self.cli_available:
            logger.error("Cannot generate text: 'gemini' CLI is missing.")
            return "Error: Gemini CLI not installed. Run: npm install -g @google/gemini-cli"

        try:
            # Adjust prompt for JSON if requested (CLI doesn't always strictly obey --output-format json for generic text)
            final_prompt = prompt
            if response_mime_type == "application/json":
                final_prompt += "\n\nIMPORTANT: Output ONLY valid JSON. No Markdown. No explanations."

            # Construct command
            # -m: Model
            # --yolo: Do not ask for confirmation
            # --output-format: text (we handle parsing if it's json)
            cmd = ["gemini", "-m", model_name, "--yolo", "--output-format", "text"]

            # Prepare Environment (Windows Fix for NPM path)
            env = os.environ.copy()
            if os.name == 'nt':
                appdata = os.getenv('APPDATA')
                if appdata:
                    npm_path = os.path.join(appdata, 'npm')
                    # Add to PATH if not present
                    if npm_path not in env.get('PATH', ''):
                        env['PATH'] = f"{npm_path};{env.get('PATH', '')}"

            # Define the subprocess runner
            def run_cli_subprocess():
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8', # Critical for Windows/Emojis
                    env=env,
                    shell=True # Critical for resolving .cmd/.bat on Windows
                )
                return process.communicate(input=final_prompt)

            # Run in thread to avoid blocking event loop
            stdout, stderr = await asyncio.to_thread(run_cli_subprocess)

            if not stdout.strip() and stderr:
                logger.warning(f"Gemini CLI stderr: {stderr}")
                # Some tools print to stderr on success, but if stdout is empty, it's likely an error
                if "error" in stderr.lower():
                    return f"Error calling Gemini CLI: {stderr}"

            # Clean result
            result = stdout.strip()
            
            # Optional: Attempt to clean markdown blocks if JSON was requested
            if response_mime_type == "application/json" and "```" in result:
                result = result.replace("```json", "").replace("```", "").strip()

            return result

        except Exception as e:
            logger.error(f"GeminiService CLI error: {e}")
            return f"Error: {str(e)}"

    async def analyze_image_style(self, image_bytes: bytes, mime_type: str) -> str:
        """
        Analyzes an image style using Gemini Vision via curl (Legacy API).
        The CLI currently does not support image inputs easily.
        """
        if not self.api_key:
            logger.error("Cannot analyze image: GEMINI_API_KEY is missing.")
            return "Error: API Key missing"

        try:
            # Encode image to base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            prompt = """Analyze the visual style of this image in detail. 
            Focus on:
            1. Lighting (natural, studio, neon, etc.)
            2. Color palette and grading
            3. Camera characteristics (film grain, bokeh, lens type)
            4. Composition and mood
            
            Summarize this into a concise \"prompt suffix\" (30-50 words) that could be used to generate similar images.
            Return ONLY the prompt suffix."""

            # Construct payload
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_b64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 200
                }
            }

            payload_json = json.dumps(payload)

            # Construct curl command
            # Using flash model for speed on images
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
            
            cmd = [
                "curl", "-X", "POST",
                url,
                "-H", "Content-Type: application/json",
                "-d", "@-" 
            ]

            # Execute subprocess
            def run_curl():
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                return process.communicate(input=payload_json)

            stdout, stderr = await asyncio.to_thread(run_curl)

            try:
                response_data = json.loads(stdout)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse API response. Stdout: {stdout}")
                return "Error: Failed to parse API response"
            
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if parts:
                        return parts[0].get('text', '').strip()
            
            if 'error' in response_data:
                logger.error(f"API Error: {response_data['error']}")
                return f"Error: {response_data['error'].get('message', 'Unknown API error')}"

            return "Error: No content generated"

        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return f"Error: {str(e)}"

    async def generate_image(
        self, 
        prompt: str, 
        aspect_ratio: str = "1:1", 
        number_of_images: int = 1
    ) -> Dict[str, Any]:
        """
        Placeholder for image generation.
        """
        logger.warning("Image generation is not fully implemented.")
        return {
            "success": False,
            "model": "placeholder",
            "images": [], 
            "message": "Image generation via CLI wrapper is not yet implemented."
        }

# Singleton instance
gemini_service = GeminiService()