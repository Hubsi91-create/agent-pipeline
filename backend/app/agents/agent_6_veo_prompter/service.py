"""
Agent 6: Veo Prompter - "The Narrative Director"
Generates narrative-style video prompts optimized for Google Veo with Few-Shot Learning
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A6_VIDEO_EXAMPLES
)
from app.utils.logger import setup_logger

logger = setup_logger("Agent6_VeoPrompter")


class Agent6VeoPrompter:
    """Singleton service for Veo prompt generation with Few-Shot Learning"""

    _instance: Optional['Agent6VeoPrompter'] = None
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
        Generate Veo-optimized narrative video prompt for a scene

        Veo Prompt Style: Narrative, flowing sentences that describe the scene
        like a director's note. Naturally integrates camera movement and style.

        Args:
            scene: Scene dict with id, start, end, type, energy, camera, lighting, description
            style: Style dict with name, suffix, negative (optional)

        Returns:
            Dict with:
            - prompt: Generated narrative prompt (max 500 chars)
            - negative: Negative prompt from style
            - model: "veo"
            - scene_id: Scene ID
        """
        logger.info(f"Generating Veo narrative prompt for scene {scene.get('id', 'unknown')}")

        try:
            # Load few-shot examples
            examples = await self._load_few_shot_examples(model="veo")

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

            generation_prompt = f"""You are a professional video director writing prompts for Google Veo.

FEW-SHOT EXAMPLES (Study these narrative patterns):
{few_shot_section}

Now generate a NARRATIVE PROMPT for:

SCENE DETAILS:
- Type: {scene_type}
- Energy: {energy}
- Camera: {camera}
- Lighting: {lighting}
- Description: {description}
- Style: {style_suffix if style_suffix else "cinematic, professional"}

REQUIREMENTS:
1. Write as FLOWING NARRATIVE (like describing a scene in a script)
2. Naturally integrate camera movement into the sentence
3. Naturally integrate lighting/mood
4. Weave in style suffix organically
5. Max 500 characters
6. Single paragraph, no bullet points
7. Focus on visual storytelling

Example format: "The camera [movement] as [subject] [action] in [environment], [lighting], [style suffix]."

Generate ONLY the narrative prompt, no explanation:"""

            # Get AI response
            ai_response = await gemini_service.generate_text(generation_prompt, temperature=0.7)

            # Clean up response
            prompt_text = ai_response.strip().replace('"', '').replace("'", "")

            # Ensure max 500 chars for Veo
            if len(prompt_text) > 500:
                prompt_text = prompt_text[:497] + "..."

            logger.info(f"Generated Veo prompt ({len(prompt_text)} chars)")

            return {
                "prompt": prompt_text,
                "negative": negative_prompt,
                "model": "veo",
                "scene_id": scene.get("id"),
                "duration": scene.get("duration", 8.0)
            }

        except Exception as e:
            logger.error(f"Veo prompt generation failed: {e}")
            # Fallback
            fallback = f"A music video scene featuring dynamic camera movement and {style_suffix if style_suffix else 'cinematic visuals'}"
            return {
                "prompt": fallback,
                "negative": negative_prompt if style else "",
                "model": "veo",
                "scene_id": scene.get("id"),
                "duration": scene.get("duration", 8.0)
            }

    async def _load_few_shot_examples(self, model: str = "veo", limit: int = 3) -> List[Dict[str, str]]:
        """
        Load few-shot examples from A6_Video_Examples Google Sheet

        Returns:
            List of example dicts with 'prompt' and 'model' keys
        """
        # Check cache
        if self._examples_cache:
            veo_examples = [e for e in self._examples_cache if e.get("model") == "veo"]
            return veo_examples[:limit]

        try:
            records = await google_sheet_service.get_all_records(SHEET_A6_VIDEO_EXAMPLES)

            if records and len(records) > 0:
                logger.info(f"Loaded {len(records)} few-shot examples from database")

                examples = []
                for record in records:
                    examples.append({
                        "model": record.get("model", "veo"),
                        "prompt": record.get("prompt", ""),
                        "category": record.get("category", "general")
                    })

                self._examples_cache = examples

                # Filter for Veo examples
                veo_examples = [e for e in examples if e.get("model") == "veo"]
                return veo_examples[:limit]

        except Exception as e:
            logger.warning(f"Could not load examples from database: {e}")

        # Fallback: Hardcoded examples
        logger.info("Using fallback few-shot examples")
        fallback_examples = [
            {
                "model": "veo",
                "prompt": "The camera slowly zooms in as the artist stands alone in a dimly lit studio, soft blue ambient light creating an intimate atmosphere, shot on CineStill 800T film with cinematic bokeh.",
                "category": "low_energy"
            },
            {
                "model": "veo",
                "prompt": "Dynamic whip pan follows the artist dancing through vibrant neon-lit streets, strobe lighting amplifying the raw energy, music video aesthetic with high contrast and colorful gels.",
                "category": "high_energy"
            },
            {
                "model": "veo",
                "prompt": "A smooth tracking shot captures the artist performing with controlled intensity, natural golden hour lighting balances energy and emotion, shot during golden hour with warm skin tones.",
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


# Singleton instance
agent6_service = Agent6VeoPrompter()
