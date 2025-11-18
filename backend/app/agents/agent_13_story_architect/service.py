"""
Agent 13: Story Architect - "The Narrative Designer"
Creates structured documentary scripts using the 3-Act structure (Netflix-style)
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger

logger = setup_logger("Agent13_StoryArchitect")


class Agent13StoryArchitect:
    """Singleton service for documentary script generation"""

    _instance: Optional['Agent13StoryArchitect'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_3_act_structure(
        self,
        topic: str,
        duration_minutes: int = 15,
        style_template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete 15-minute documentary script using 3-Act structure

        3-Act Structure:
        - Act 1 (Hook): 0-2 minutes - Grab attention, establish stakes
        - Act 2 (Conflict): 2-10 minutes - Explore the problem/journey
        - Act 3 (Resolution): 10-15 minutes - Provide answers/conclusion

        Args:
            topic: Documentary topic (e.g., "The Rise of AI")
            duration_minutes: Total duration (default: 15)
            style_template: Optional style template from Agent 12

        Returns:
            Complete documentary script with:
            - chapters: List of chapter objects with timing
            - narration: Full narrator script
            - b_roll: B-roll suggestions for each chapter
            - structure: 3-act breakdown
        """
        logger.info(f"Creating 3-act structure for topic: '{topic}'")

        # Use style template if provided, otherwise use defaults
        narrative_style = "Informative"
        mood = "Professional"
        if style_template:
            narrative_style = style_template.get("tone", {}).get("narrative_style", "Informative")
            mood = style_template.get("tone", {}).get("mood", "Professional")

        # Generate script with Gemini
        script = await self._generate_script_with_ai(
            topic=topic,
            duration_minutes=duration_minutes,
            narrative_style=narrative_style,
            mood=mood,
            style_template=style_template
        )

        logger.info(f"Script generated: {len(script.get('chapters', []))} chapters")
        return script

    async def _generate_script_with_ai(
        self,
        topic: str,
        duration_minutes: int,
        narrative_style: str,
        mood: str,
        style_template: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use Gemini Pro to generate the complete documentary script

        Args:
            topic: Documentary topic
            duration_minutes: Total duration
            narrative_style: Style of narration
            mood: Emotional tone
            style_template: Optional style template

        Returns:
            Complete script structure
        """
        # Build style context
        style_context = ""
        if style_template:
            style_context = f"""
**Style Template** (clone this style):
- Template: {style_template.get('template_name', 'N/A')}
- Narrative: {narrative_style}
- Mood: {mood}
- Pacing: {style_template.get('pacing', {}).get('words_per_minute', 150)} WPM
- B-Roll Frequency: {style_template.get('visual_style', {}).get('b_roll_frequency', 'Every 10-15 seconds')}
"""
        else:
            style_context = f"""
**Style Guidelines**:
- Narrative: {narrative_style}
- Mood: {mood}
- Pacing: ~150 words per minute
- B-Roll: Every 10-15 seconds
"""

        script_prompt = f"""You are a professional documentary scriptwriter for Netflix-style productions.

Create a {duration_minutes}-minute documentary script about: **{topic}**

{style_context}

**3-Act Structure Requirements:**

**ACT 1: THE HOOK** (0-2 minutes, ~300 words)
- Open with a compelling hook that grabs attention immediately
- Establish the stakes: Why does this topic matter?
- Introduce the central question or conflict
- Create emotional connection with the audience

**ACT 2: THE CONFLICT/JOURNEY** (2-10 minutes, ~1200 words)
- Dive deep into the problem, history, or journey
- Present multiple perspectives or complications
- Build tension and intrigue
- Use storytelling to maintain engagement
- Include turning points or revelations

**ACT 3: THE RESOLUTION** (10-15 minutes, ~750 words)
- Provide answers, solutions, or insights
- Tie back to the opening hook
- Deliver satisfying conclusion
- Leave audience with something to think about
- End on a strong, memorable note

**Output Format (JSON):**
{{
  "title": "Documentary title",
  "logline": "One-sentence description",
  "total_duration_minutes": {duration_minutes},
  "total_word_count": 2250,
  "structure": {{
    "act_1": {{
      "title": "The Hook",
      "duration_range": "0:00-2:00",
      "objective": "...",
      "key_points": ["...", "...", "..."]
    }},
    "act_2": {{
      "title": "The Conflict",
      "duration_range": "2:00-10:00",
      "objective": "...",
      "key_points": ["...", "...", "..."]
    }},
    "act_3": {{
      "title": "The Resolution",
      "duration_range": "10:00-15:00",
      "objective": "...",
      "key_points": ["...", "...", "..."]
    }}
  }},
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "...",
      "start_time": "0:00",
      "end_time": "2:00",
      "act": 1,
      "narration": "Full narrator script for this chapter (300 words)...",
      "b_roll_shots": [
        "Shot 1 description",
        "Shot 2 description",
        "Shot 3 description"
      ],
      "key_visuals": "Main visual focus"
    }},
    {{
      "chapter_number": 2,
      "title": "...",
      "start_time": "2:00",
      "end_time": "5:00",
      "act": 2,
      "narration": "Full narrator script (450 words)...",
      "b_roll_shots": ["...", "...", "..."],
      "key_visuals": "..."
    }}
    // ... continue for all chapters (aim for 5-7 total chapters)
  ]
}}

**Important:**
- Write in {narrative_style.lower()} style
- Maintain {mood.lower()} tone throughout
- Each chapter should have FULL narrator script (not just bullet points)
- B-roll shots should be specific and actionable
- Ensure smooth transitions between chapters
- Total word count should be ~2250 words ({duration_minutes} min × 150 wpm)

Generate the complete documentary script now:"""

        try:
            response = await gemini_service.generate_text(
                script_prompt,
                temperature=0.8,  # Higher creativity for storytelling
                max_tokens=8000    # Need space for full script
            )

            # Try to parse JSON from response
            import json
            import re

            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                script_data = json.loads(json_match.group())

                # Add metadata
                script_data["topic"] = topic
                script_data["success"] = True
                script_data["generated_at"] = self._get_timestamp()

                logger.info(f"Script generated successfully: {script_data.get('title')}")
                return script_data
            else:
                logger.warning("Could not parse JSON from AI response, using fallback")
                return self._generate_fallback_script(topic, duration_minutes)

        except Exception as e:
            logger.error(f"AI script generation failed: {e}")
            return self._generate_fallback_script(topic, duration_minutes)

    def _generate_fallback_script(
        self,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Generate fallback script when AI generation fails"""
        return {
            "success": True,
            "topic": topic,
            "title": f"The Story of {topic}",
            "logline": f"An in-depth exploration of {topic} and its impact on our world",
            "total_duration_minutes": duration_minutes,
            "total_word_count": duration_minutes * 150,
            "structure": {
                "act_1": {
                    "title": "The Hook",
                    "duration_range": "0:00-2:00",
                    "objective": "Grab attention and establish stakes",
                    "key_points": [
                        "Open with compelling question",
                        "Introduce the topic's relevance",
                        "Establish emotional connection"
                    ]
                },
                "act_2": {
                    "title": "The Journey",
                    "duration_range": "2:00-10:00",
                    "objective": "Explore the topic in depth",
                    "key_points": [
                        "Present historical context",
                        "Explore different perspectives",
                        "Build complexity and intrigue"
                    ]
                },
                "act_3": {
                    "title": "The Resolution",
                    "duration_range": "10:00-15:00",
                    "objective": "Provide insights and conclusion",
                    "key_points": [
                        "Tie themes together",
                        "Provide actionable insights",
                        "End with memorable takeaway"
                    ]
                }
            },
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Opening Hook",
                    "start_time": "0:00",
                    "end_time": "2:00",
                    "act": 1,
                    "narration": f"What if I told you that {topic} is changing the world in ways you never imagined? From the way we work to how we think, this force is reshaping our reality. But to understand where we're going, we need to understand where we've been. This is the story of {topic}.",
                    "b_roll_shots": [
                        f"Montage of {topic} in action",
                        "Close-up of key elements",
                        "Wide establishing shot"
                    ],
                    "key_visuals": "Dramatic opening sequence"
                },
                {
                    "chapter_number": 2,
                    "title": "The Origins",
                    "start_time": "2:00",
                    "end_time": "5:00",
                    "act": 2,
                    "narration": f"To understand {topic}, we must go back to its beginnings. The seeds of this revolution were planted decades ago...",
                    "b_roll_shots": [
                        "Archival footage",
                        "Historical timeline graphics",
                        "Key figures and moments"
                    ],
                    "key_visuals": "Historical context"
                },
                {
                    "chapter_number": 3,
                    "title": "The Turning Point",
                    "start_time": "5:00",
                    "end_time": "10:00",
                    "act": 2,
                    "narration": f"But everything changed when... The implications of {topic} became impossible to ignore.",
                    "b_roll_shots": [
                        "Dramatic transition shots",
                        "Modern examples",
                        "Expert interviews"
                    ],
                    "key_visuals": "Pivotal moment"
                },
                {
                    "chapter_number": 4,
                    "title": "The Future Ahead",
                    "start_time": "10:00",
                    "end_time": "15:00",
                    "act": 3,
                    "narration": f"So where do we go from here? The future of {topic} is being written right now, by people like you. The question isn't whether {topic} will shape our world—it's how we'll shape it.",
                    "b_roll_shots": [
                        "Future-focused imagery",
                        "Inspirational shots",
                        "Closing montage"
                    ],
                    "key_visuals": "Hopeful conclusion"
                }
            ],
            "generated_at": self._get_timestamp(),
            "note": "Fallback script generated. For best results, configure GEMINI_API_KEY."
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton instance
agent13_service = Agent13StoryArchitect()
