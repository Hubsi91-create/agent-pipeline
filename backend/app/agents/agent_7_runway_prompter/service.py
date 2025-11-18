"""
Agent 7: Runway Prompter - "The Motion Specialist"
Generates modular, comma-separated prompts optimized for Runway Gen-4 with Few-Shot Learning
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A6_VIDEO_EXAMPLES
)
from app.utils.logger import setup_logger

logger = setup_logger("Agent7_RunwayPrompter")


class Agent7RunwayPrompter:
    """Singleton service for Runway prompt generation with Few-Shot Learning"""

    _instance: Optional['Agent7RunwayPrompter'] = None
    _examples_cache: Optional[List[Dict[str, str]]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def generate_prompt(
        self,
        scene: Dict[str, Any],
        style: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate Runway-optimized modular video prompt for a scene

        Runway Prompt Style: Modular, comma-separated structure that clearly
        defines subject, motion, camera, environment, and style in distinct segments.

        Structure: [Subject Motion], [Camera Move], [Environment], [Style Suffix]

        Args:
            scene: Scene dict with id, start, end, type, energy, camera, lighting, description
            style: Style dict with name, suffix, negative (optional)

        Returns:
            Dict with:
            - prompt: Generated modular prompt (max 300 chars)
            - negative: Negative prompt from style
            - model: "runway"
            - scene_id: Scene ID
        """
        logger.info(f"Generating Runway modular prompt for scene {scene.get('id', 'unknown')}")

        try:
            # Load few-shot examples
            examples = await self._load_few_shot_examples(model="runway")

            # Build few-shot prompt
            few_shot_section = self._build_few_shot_section(examples)

            # Build the generation prompt
            scene_type = scene.get("type", "Scene")
            energy = scene.get("energy", "Medium")
            camera = scene.get("camera", "Static")
            lighting = scene.get("lighting", "Natural")
            description = scene.get("description", "Artist performs")

            # Style suffix (if provided)
            style_suffix = ""
            negative_prompt = ""
            if style:
                style_suffix = style.get("suffix", "")
                negative_prompt = style.get("negative", "")

            generation_prompt = f"""You are a professional video prompter writing for Runway Gen-4.

FEW-SHOT EXAMPLES (Study these modular patterns):
{few_shot_section}

Now generate a MODULAR PROMPT for:

SCENE DETAILS:
- Type: {scene_type}
- Energy: {energy}
- Camera: {camera}
- Lighting: {lighting}
- Description: {description}
- Style: {style_suffix if style_suffix else "cinematic, professional"}

REQUIREMENTS:
1. Write as COMMA-SEPARATED MODULES (not narrative)
2. Structure: [Subject Motion], [Camera Movement], [Environment/Lighting], [Style Suffix]
3. Each module is a concise phrase
4. Emphasize motion and dynamics (Runway excels at motion)
5. Max 300 characters total
6. No full sentences, just keyword-rich descriptive phrases

Example format: "Artist dancing energetically, rapid whip pan camera, vibrant neon-lit urban environment, high contrast colorful gels, music video aesthetic"

Generate ONLY the modular prompt, no explanation:"""

            # Get AI response
            ai_response = await gemini_service.generate_text(generation_prompt, temperature=0.7)

            # Clean up response
            prompt_text = ai_response.strip().replace('"', '').replace("'", "")

            # Ensure max 300 chars for Runway
            if len(prompt_text) > 300:
                prompt_text = prompt_text[:297] + "..."

            logger.info(f"Generated Runway prompt ({len(prompt_text)} chars)")

            return {
                "prompt": prompt_text,
                "negative": negative_prompt,
                "model": "runway",
                "scene_id": scene.get("id"),
                "duration": min(scene.get("duration", 8.0), 10.0)  # Runway Gen-4 supports up to 10s
            }

        except Exception as e:
            logger.error(f"Runway prompt generation failed: {e}")
            # Fallback
            fallback = f"Artist performing, {camera.lower()} camera, {lighting.lower()} lighting, {style_suffix if style_suffix else 'cinematic quality'}"
            return {
                "prompt": fallback,
                "negative": negative_prompt if style else "",
                "model": "runway",
                "scene_id": scene.get("id"),
                "duration": min(scene.get("duration", 8.0), 10.0)
            }

    async def _load_few_shot_examples(self, model: str = "runway", limit: int = 3) -> List[Dict[str, str]]:
        """
        Load few-shot examples from A6_Video_Examples Google Sheet

        Returns:
            List of example dicts with 'prompt' and 'model' keys
        """
        # Check cache
        if self._examples_cache:
            runway_examples = [e for e in self._examples_cache if e.get("model") == "runway"]
            return runway_examples[:limit]

        try:
            records = await google_sheet_service.get_all_records(SHEET_A6_VIDEO_EXAMPLES)

            if records and len(records) > 0:
                logger.info(f"Loaded {len(records)} few-shot examples from database")

                examples = []
                for record in records:
                    examples.append({
                        "model": record.get("model", "runway"),
                        "prompt": record.get("prompt", ""),
                        "category": record.get("category", "general")
                    })

                self._examples_cache = examples

                # Filter for Runway examples
                runway_examples = [e for e in examples if e.get("model") == "runway"]
                return runway_examples[:limit]

        except Exception as e:
            logger.warning(f"Could not load examples from database: {e}")

        # Fallback: Hardcoded examples
        logger.info("Using fallback few-shot examples")
        fallback_examples = [
            {
                "model": "runway",
                "prompt": "Artist standing contemplatively, slow zoom in camera, dimly lit studio with soft blue ambient light, intimate atmosphere, shot on CineStill 800T film, cinematic bokeh",
                "category": "low_energy"
            },
            {
                "model": "runway",
                "prompt": "Artist dancing energetically through streets, dynamic whip pan camera, vibrant neon-lit urban environment, strobe lighting effects, high contrast music video aesthetic, colorful gels",
                "category": "high_energy"
            },
            {
                "model": "runway",
                "prompt": "Artist performing with controlled movement, smooth tracking shot camera, natural golden hour lighting, warm skin tones, balanced energy, professional production quality",
                "category": "medium_energy"
            }
        ]

        return fallback_examples[:limit]

    def _build_few_shot_section(self, examples: List[Dict[str, str]]) -> str:
        """Build few-shot examples section for the prompt"""
        if not examples:
            return "No examples available."

        lines = []
        for idx, example in enumerate(examples, 1):
            lines.append(f"Example {idx}: \"{example.get('prompt', '')}\"")

        return "\n".join(lines)

    async def save_as_gold_standard(
        self,
        prompt: str,
        scene_description: str,
        energy: str = "medium"
    ) -> Dict[str, Any]:
        """
        Save a generated prompt as a gold standard example (Feedback Loop)

        This enables the system to learn from its own successes.
        Good prompts are saved to A6_Video_Examples and become part
        of the Few-Shot Learning knowledge base for future generations.

        Args:
            prompt: The generated Runway prompt to save
            scene_description: Brief description of the scene
            energy: Energy level (low, medium, high)

        Returns:
            Dict with success status and message
        """
        logger.info(f"Saving Runway prompt as gold standard: {prompt[:50]}...")

        try:
            from datetime import datetime

            # Prepare data for A6_Video_Examples sheet
            timestamp = datetime.now().isoformat()
            data = [
                "runway",  # model
                prompt,  # prompt
                energy,  # category/energy level
                scene_description,  # description
                timestamp,  # created_at
                "auto-learned"  # source
            ]

            # Append to Google Sheets
            success = await google_sheet_service.append_row(
                SHEET_A6_VIDEO_EXAMPLES,
                data
            )

            if success:
                # Clear cache to force reload with new example
                self._examples_cache = None

                logger.info(f"✅ Runway prompt saved to gold standards")
                return {
                    "success": True,
                    "message": "Prompt added to Few-Shot Learning database",
                    "model": "runway"
                }
            else:
                logger.error("Failed to save prompt to database")
                return {
                    "success": False,
                    "message": "Failed to save to database"
                }

        except Exception as e:
            logger.error(f"Error saving gold standard: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }


# Singleton instance
agent7_service = Agent7RunwayPrompter()
