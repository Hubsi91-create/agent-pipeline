"""
Suno Prompt Generator Service - Dynamic Few-Shot Learning
Generates Suno v5 prompts using in-context learning from best practices
"""

import random
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.data_models import (
    SunoPromptRequest,
    SunoPromptResponse,
    SunoPromptExample,
    FewShotLearningStats
)
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_SUNO_PROMPTS,
    SHEET_APPROVED_BEST_PRACTICES
)
from app.utils.logger import setup_logger

logger = setup_logger("SunoPromptGenerator")


class SunoPromptGeneratorService:
    """
    Singleton service for Suno prompt generation with Dynamic Few-Shot Learning

    Key Concept: Instead of training a model, we dynamically inject best practice
    examples into the prompt context. The system "learns" by accumulating excellent
    examples in the ApprovedBestPractices sheet.
    """

    _instance: Optional['SunoPromptGeneratorService'] = None

    # Fallback examples if sheet is empty (seed knowledge)
    FALLBACK_EXAMPLES = [
        SunoPromptExample(
            prompt_text="[Verse]\nNeon lights paint the night in electric blue\nCity pulse beats fast beneath my worn-out shoes\nChasing dreams through concrete canyons deep and wide\nLost souls dance together in the urban tide",
            genre="Electronic Pop",
            quality_score=8.5,
            tags=["urban", "energetic", "modern"],
            source="seed"
        ),
        SunoPromptExample(
            prompt_text="[Chorus]\nThunder rolling over distant mountains high\nRaindrops falling like tears from the sky\nNature's symphony in perfect harmony\nEchoes of forever in this melody",
            genre="Folk",
            quality_score=8.0,
            tags=["nature", "atmospheric", "emotional"],
            source="seed"
        ),
        SunoPromptExample(
            prompt_text="[Bridge]\nBass drops heavy like my heart tonight\nSynths cutting through the darkness bright\nLost in rhythm, found in sound\nWhere broken pieces can be found",
            genre="EDM",
            quality_score=9.0,
            tags=["intense", "dynamic", "powerful"],
            source="seed"
        )
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def generate_prompt(self, request: SunoPromptRequest) -> SunoPromptResponse:
        """
        Generate Suno prompt using Few-Shot Learning

        Process:
        1. Fetch 3-5 best practice examples from ApprovedBestPractices sheet
        2. Inject these examples into the system prompt
        3. Ask Gemini to generate a new prompt following these patterns
        4. Return the generated prompt (pending QC)
        """
        logger.info(f"Generating Suno prompt for genre: {request.target_genre}")

        # Step 1: Get Few-Shot examples
        examples = await self._get_few_shot_examples(
            target_genre=request.target_genre,
            num_examples=5
        )

        # Step 2: Build enhanced system prompt with examples
        system_prompt = self._build_few_shot_prompt(examples, request)

        # Step 3: Generate with Gemini
        try:
            generated_text = await gemini_service.generate_text(
                system_prompt,
                temperature=0.8,  # Higher creativity for artistic content
                max_tokens=1024
            )

            # Step 4: Create response
            response = SunoPromptResponse(
                prompt_text=generated_text.strip(),
                genre=request.target_genre,
                mood=request.mood,
                tempo=request.tempo,
                few_shot_examples_used=len(examples),
                status="PENDING_QC"
            )

            # Step 5: Save to Suno_Prompts_DB
            await self._save_to_sheets(response)

            logger.info(f"Generated prompt {response.id} using {len(examples)} examples")
            return response

        except Exception as e:
            logger.error(f"Failed to generate Suno prompt: {e}")
            raise

    async def _get_few_shot_examples(
        self,
        target_genre: Optional[str] = None,
        num_examples: int = 5
    ) -> List[SunoPromptExample]:
        """
        Retrieve Few-Shot Learning examples from ApprovedBestPractices sheet

        Selection Strategy:
        1. Prefer examples with quality_score >= 8.0
        2. Prefer examples from the same genre (if specified)
        3. Include some cross-genre examples for creativity
        4. Randomize to avoid overfitting
        """
        try:
            # Get all approved examples from sheet
            records = await google_sheet_service.get_all_records(SHEET_APPROVED_BEST_PRACTICES)

            if not records:
                logger.warning("ApprovedBestPractices sheet is empty, using fallback examples")
                return self.FALLBACK_EXAMPLES[:num_examples]

            # Parse records into SunoPromptExample objects
            examples = []
            for record in records:
                try:
                    example = SunoPromptExample(
                        id=record.get("id", ""),
                        prompt_text=record.get("prompt_text", ""),
                        genre=record.get("genre", ""),
                        quality_score=float(record.get("quality_score", 0)),
                        tags=record.get("tags", "").split(",") if record.get("tags") else [],
                        created_at=datetime.fromisoformat(record.get("created_at", datetime.utcnow().isoformat())),
                        source=record.get("source", "generated")
                    )

                    # Only include high-quality examples
                    if example.quality_score >= 8.0:
                        examples.append(example)
                except Exception as e:
                    logger.warning(f"Failed to parse example: {e}")
                    continue

            if not examples:
                logger.warning("No high-quality examples found, using fallback")
                return self.FALLBACK_EXAMPLES[:num_examples]

            # Selection strategy
            selected = []

            # 1. Prefer same genre (60% of examples)
            if target_genre:
                same_genre = [ex for ex in examples if ex.genre.lower() == target_genre.lower()]
                genre_count = int(num_examples * 0.6)
                if same_genre:
                    selected.extend(random.sample(same_genre, min(genre_count, len(same_genre))))

            # 2. Fill remaining with diverse examples (40% for creativity)
            remaining_count = num_examples - len(selected)
            if remaining_count > 0:
                other_examples = [ex for ex in examples if ex not in selected]
                if other_examples:
                    selected.extend(random.sample(other_examples, min(remaining_count, len(other_examples))))

            # 3. If still not enough, use fallback
            if len(selected) < num_examples:
                fallback_needed = num_examples - len(selected)
                selected.extend(self.FALLBACK_EXAMPLES[:fallback_needed])

            logger.info(f"Selected {len(selected)} Few-Shot examples (target genre: {target_genre})")
            return selected[:num_examples]

        except Exception as e:
            logger.error(f"Failed to get Few-Shot examples: {e}")
            return self.FALLBACK_EXAMPLES[:num_examples]

    def _build_few_shot_prompt(
        self,
        examples: List[SunoPromptExample],
        request: SunoPromptRequest
    ) -> str:
        """
        Build the Few-Shot Learning prompt for Gemini

        Structure:
        1. System role definition
        2. Few-Shot examples (the "learning" part)
        3. Task specification
        4. Output format instructions
        """
        # Format examples
        examples_text = "\n\n".join([
            f"EXAMPLE {i+1} (Genre: {ex.genre}, Quality: {ex.quality_score}/10):\n{ex.prompt_text}"
            for i, ex in enumerate(examples)
        ])

        # Build additional context
        context_parts = []
        if request.mood:
            context_parts.append(f"Mood: {request.mood}")
        if request.tempo:
            context_parts.append(f"Tempo: {request.tempo}")
        if request.style_references:
            context_parts.append(f"Style References: {', '.join(request.style_references)}")
        if request.additional_instructions:
            context_parts.append(f"Additional: {request.additional_instructions}")

        context = "\n".join(context_parts) if context_parts else "Creative freedom encouraged"

        # The Few-Shot prompt
        prompt = f"""You are an expert Suno v5 prompt engineer specializing in creating engaging, high-quality music prompts.

**LEARN FROM THESE BEST PRACTICE EXAMPLES:**

{examples_text}

---

**YOUR TASK:**
Generate a NEW Suno v5 prompt for the following requirements:

Genre: {request.target_genre}
{context}

**QUALITY STANDARDS (learned from examples above):**
1. Use clear structure markers ([Verse], [Chorus], [Bridge])
2. Create vivid, sensory imagery
3. Maintain consistent theme and emotion
4. Use poetic but accessible language
5. Include dynamic contrast between sections
6. Keep lines concise and rhythmic

**OUTPUT:**
Generate ONLY the prompt text (with structure markers). Make it unique while following the quality patterns from the examples.

Prompt:"""

        return prompt

    async def _save_to_sheets(self, response: SunoPromptResponse) -> bool:
        """Save generated prompt to Suno_Prompts_DB"""
        data = [
            response.id,
            response.prompt_text[:500],  # Truncate for sheet
            response.genre,
            response.mood or "",
            response.tempo or "",
            response.few_shot_examples_used,
            response.quality_score or 0,
            response.status,
            response.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_SUNO_PROMPTS, data)

    async def get_learning_stats(self) -> FewShotLearningStats:
        """
        Get statistics about the Few-Shot Learning system
        Shows how the system is "learning" over time
        """
        try:
            records = await google_sheet_service.get_all_records(SHEET_APPROVED_BEST_PRACTICES)

            if not records:
                return FewShotLearningStats(
                    total_examples=len(self.FALLBACK_EXAMPLES),
                    avg_quality_score=8.5,
                    examples_by_genre={"Seed Examples": len(self.FALLBACK_EXAMPLES)},
                    recent_additions=0,
                    top_performing_genres=["Electronic Pop", "Folk", "EDM"]
                )

            # Calculate stats
            total = len(records)
            scores = [float(r.get("quality_score", 0)) for r in records]
            avg_score = sum(scores) / len(scores) if scores else 0

            # By genre
            by_genre = {}
            for r in records:
                genre = r.get("genre", "Unknown")
                by_genre[genre] = by_genre.get(genre, 0) + 1

            # Recent additions (last 24h)
            recent_count = 0
            cutoff = datetime.utcnow() - timedelta(hours=24)
            for r in records:
                try:
                    created = datetime.fromisoformat(r.get("created_at", ""))
                    if created > cutoff:
                        recent_count += 1
                except:
                    pass

            # Top performing
            top_genres = sorted(by_genre.items(), key=lambda x: x[1], reverse=True)[:5]

            return FewShotLearningStats(
                total_examples=total,
                avg_quality_score=round(avg_score, 2),
                examples_by_genre=by_genre,
                recent_additions=recent_count,
                top_performing_genres=[g[0] for g in top_genres]
            )

        except Exception as e:
            logger.error(f"Failed to get learning stats: {e}")
            raise


# Singleton instance
suno_generator_service = SunoPromptGeneratorService()
