"""
Dadan AI Metadata Service - YouTube Optimization
=================================================
Generates SEO-optimized YouTube metadata for music videos.

Features:
- YouTube Title Generation
- Description with Keywords
- Tag Generation
- Hashtag Optimization
- Trending Score Calculation
- Caching (30-day TTL)

Author: Music Video Production System
Version: 1.0.0
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DadanService:
    """
    Dadan AI Metadata Generation Service

    Provides methods for:
    - YouTube title generation
    - Description creation
    - Tag/hashtag optimization
    - Trending score analysis
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Dadan Service

        Args:
            api_key: Dadan API key (optional)
        """
        self.api_key = api_key
        self.api_base = "https://api.dadan.ai/v1"

        # In-memory cache (in production, use Redis)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(days=30)

        # Genre-based keywords
        self.genre_keywords = {
            'electronic': ['edm', 'dance', 'club', 'festival', 'bass', 'drop'],
            'hip-hop': ['rap', 'beats', 'freestyle', 'trap', 'bars', 'flow'],
            'pop': ['catchy', 'hit', 'radio', 'chart', 'mainstream', 'viral'],
            'rock': ['guitar', 'drums', 'band', 'live', 'energy', 'power'],
            'classical': ['orchestra', 'symphony', 'piano', 'violin', 'maestro'],
            'jazz': ['smooth', 'saxophone', 'improvisation', 'swing', 'blues'],
            'ambient': ['chill', 'relaxing', 'meditation', 'peaceful', 'calm'],
            'metal': ['heavy', 'brutal', 'headbang', 'mosh', 'aggressive'],
            'indie': ['alternative', 'underground', 'unique', 'artistic']
        }

        # Mood-based modifiers
        self.mood_modifiers = {
            'happy': ['upbeat', 'positive', 'feel-good', 'energetic', 'joyful'],
            'sad': ['emotional', 'melancholic', 'deep', 'touching', 'heartfelt'],
            'energetic': ['powerful', 'intense', 'dynamic', 'explosive', 'hype'],
            'calm': ['peaceful', 'serene', 'tranquil', 'soothing', 'ambient'],
            'dark': ['mysterious', 'moody', 'atmospheric', 'haunting', 'noir'],
            'epic': ['cinematic', 'dramatic', 'grand', 'orchestral', 'legendary']
        }

    def _get_cache_key(self, song_title: str, genre: str) -> str:
        """Generate cache key"""
        key_string = f"{song_title}_{genre}".lower()
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata from cache"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['cached_at'])

            # Check if cache is still valid
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_data['metadata']
            else:
                # Remove expired cache
                del self.cache[cache_key]
                logger.info(f"Cache expired for key: {cache_key}")

        return None

    def _save_to_cache(self, cache_key: str, metadata: Dict[str, Any]):
        """Save metadata to cache"""
        self.cache[cache_key] = {
            'metadata': metadata,
            'cached_at': datetime.now().isoformat()
        }
        logger.info(f"Cached metadata for key: {cache_key}")

    def generate_metadata(
        self,
        song_title: str,
        genre: str,
        mood: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate YouTube metadata

        Args:
            song_title: Song title
            genre: Music genre
            mood: Song mood (optional)

        Returns:
            YouTube metadata dictionary
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(song_title, genre)
            cached_metadata = self._get_from_cache(cache_key)

            if cached_metadata:
                return {
                    **cached_metadata,
                    'from_cache': True
                }

            # Generate metadata
            year = datetime.now().year
            genre_clean = genre.lower()
            mood_clean = mood.lower() if mood else 'energetic'

            # Generate title
            youtube_title = self._generate_title(song_title, genre_clean, year)

            # Generate description
            youtube_description = self._generate_description(
                song_title, genre_clean, mood_clean
            )

            # Generate tags
            youtube_tags = self._generate_tags(song_title, genre_clean, mood_clean)

            # Generate hashtags
            youtube_hashtags = self._generate_hashtags(genre_clean, mood_clean)

            # Calculate trending score
            trending_score = self._calculate_trending_score(
                song_title, genre_clean, mood_clean
            )

            metadata = {
                'youtube_title': youtube_title,
                'youtube_description': youtube_description,
                'youtube_tags': youtube_tags,
                'youtube_hashtags': youtube_hashtags,
                'trending_score': trending_score,
                'genre': genre,
                'mood': mood,
                'generated_at': datetime.now().isoformat(),
                'from_cache': False
            }

            # Save to cache
            self._save_to_cache(cache_key, metadata)

            return metadata

        except Exception as e:
            logger.error(f"Metadata generation failed: {str(e)}")
            return {
                'error': 'METADATA_GENERATION_FAILED',
                'message': str(e),
                'retryable': True
            }

    def _generate_title(self, song_title: str, genre: str, year: int) -> str:
        """
        Generate YouTube-optimized title

        Args:
            song_title: Song title
            genre: Music genre
            year: Current year

        Returns:
            Optimized title
        """
        # Add emoji and branding
        emoji_map = {
            'electronic': '🎵',
            'hip-hop': '🎤',
            'pop': '⭐',
            'rock': '🎸',
            'classical': '🎼',
            'jazz': '🎷',
            'ambient': '🌊',
            'metal': '⚡',
            'indie': '🎨'
        }

        emoji = emoji_map.get(genre, '🎵')
        genre_capitalized = genre.replace('-', ' ').title()

        # Format: 🎵 Song Title | Genre Mix 2024
        title = f"{emoji} {song_title} | {genre_capitalized} Mix {year}"

        return title

    def _generate_description(
        self,
        song_title: str,
        genre: str,
        mood: str
    ) -> str:
        """
        Generate YouTube description with keywords

        Args:
            song_title: Song title
            genre: Music genre
            mood: Song mood

        Returns:
            Optimized description
        """
        genre_keywords = self.genre_keywords.get(genre, [])
        mood_keywords = self.mood_modifiers.get(mood, [])

        description_parts = [
            f"🎵 {song_title}",
            "",
            f"Experience this {mood} {genre} track that combines",
            f"{', '.join(genre_keywords[:3])} with {', '.join(mood_keywords[:2])} vibes.",
            "",
            "Perfect for:",
            f"• {genre.title()} music lovers",
            f"• {mood.title()} playlist enthusiasts",
            "• Music video creators",
            "• Content creators looking for background music",
            "",
            "🔔 Subscribe for more music content!",
            "👍 Like if you enjoyed this track!",
            "💬 Comment your thoughts below!",
            "",
            f"#music #{genre.replace(' ', '')} #{mood} #musicvideo",
            "",
            "---",
            "Generated by Music Agents Production System",
            "AI-powered music video creation platform"
        ]

        return "\n".join(description_parts)

    def _generate_tags(
        self,
        song_title: str,
        genre: str,
        mood: str
    ) -> str:
        """
        Generate YouTube tags

        Args:
            song_title: Song title
            genre: Music genre
            mood: Song mood

        Returns:
            Comma-separated tags
        """
        tags = []

        # Base tags
        tags.append(song_title.lower())
        tags.append(genre)
        tags.append(mood)

        # Genre-specific tags
        genre_tags = self.genre_keywords.get(genre, [])
        tags.extend(genre_tags[:5])

        # Mood-specific tags
        mood_tags = self.mood_modifiers.get(mood, [])
        tags.extend(mood_tags[:3])

        # General music tags
        general_tags = [
            'music',
            'music video',
            f'{genre} music',
            f'{mood} music',
            'new music',
            f'{datetime.now().year} music'
        ]
        tags.extend(general_tags)

        # Remove duplicates and limit to 30 tags
        unique_tags = list(dict.fromkeys(tags))[:30]

        return ', '.join(unique_tags)

    def _generate_hashtags(self, genre: str, mood: str) -> str:
        """
        Generate trending hashtags

        Args:
            genre: Music genre
            mood: Song mood

        Returns:
            Space-separated hashtags
        """
        hashtags = [
            '#music',
            f'#{genre.replace(" ", "")}',
            f'#{mood}',
            '#musicvideo',
            '#newmusic',
            '#trending',
            f'#{genre.replace(" ", "")}music',
            '#viral',
            '#ai',
            '#musicproduction'
        ]

        return ' '.join(hashtags[:10])

    def _calculate_trending_score(
        self,
        song_title: str,
        genre: str,
        mood: str
    ) -> int:
        """
        Calculate trending score (0-100)

        Args:
            song_title: Song title
            genre: Music genre
            mood: Song mood

        Returns:
            Trending score (0-100)
        """
        score = 50  # Base score

        # Genre popularity
        popular_genres = ['pop', 'hip-hop', 'electronic', 'indie']
        if genre in popular_genres:
            score += 15

        # Mood appeal
        appealing_moods = ['happy', 'energetic', 'epic']
        if mood in appealing_moods:
            score += 10

        # Title length (shorter is better for virality)
        title_length = len(song_title)
        if title_length < 20:
            score += 10
        elif title_length > 40:
            score -= 5

        # Keyword presence
        viral_keywords = ['love', 'night', 'dream', 'fire', 'summer', 'dance']
        title_lower = song_title.lower()
        keyword_matches = sum(1 for keyword in viral_keywords if keyword in title_lower)
        score += keyword_matches * 5

        # Ensure score is within 0-100
        score = max(0, min(100, score))

        return score

    def clear_cache(self):
        """Clear metadata cache"""
        self.cache.clear()
        logger.info("Metadata cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Cache statistics
        """
        total_entries = len(self.cache)
        expired_count = 0

        for cache_key, cached_data in self.cache.items():
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now() - cached_time >= self.cache_ttl:
                expired_count += 1

        return {
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'active_entries': total_entries - expired_count,
            'cache_ttl_days': self.cache_ttl.days
        }


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def create_dadan_service(api_key: Optional[str] = None) -> DadanService:
    """
    Factory function to create Dadan service

    Args:
        api_key: Dadan API key (optional)

    Returns:
        Configured DadanService instance
    """
    return DadanService(api_key=api_key)


def get_supported_genres() -> List[str]:
    """
    Get list of supported genres

    Returns:
        List of genre identifiers
    """
    service = DadanService()
    return list(service.genre_keywords.keys())


def get_supported_moods() -> List[str]:
    """
    Get list of supported moods

    Returns:
        List of mood identifiers
    """
    service = DadanService()
    return list(service.mood_modifiers.keys())
