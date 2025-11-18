"""
Agent 16: Stock Scout

Finds free stock footage and images for documentary B-roll.
Uses Pexels API (and optionally Pixabay) for royalty-free content.
"""

import logging
from typing import Dict, Any, List, Optional
import os
import requests

logger = logging.getLogger(__name__)


class StockScoutService:
    """Agent 16: Find free stock footage for B-roll"""

    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pexels_base_url = "https://api.pexels.com/v1"
        self.pexels_videos_url = "https://api.pexels.com/videos"
        logger.info("Agent 16 (Stock Scout) initialized")

    async def find_stock_footage(
        self,
        keywords: List[str],
        media_type: str = "videos",
        results_per_keyword: int = 3
    ) -> Dict[str, Any]:
        """
        Find stock footage based on B-roll keywords

        Args:
            keywords: List of search terms from script
            media_type: "videos" or "photos"
            results_per_keyword: Number of results per keyword

        Returns:
            {
                "success": bool,
                "results": List[Dict],  # Video/photo results
                "total_found": int,
                "keywords_searched": List[str]
            }
        """
        try:
            if not self.pexels_api_key:
                logger.warning("Pexels API key not set, using mockup data")
                return self._get_mockup_results(keywords, media_type)

            all_results = []

            for keyword in keywords[:10]:  # Limit to 10 keywords to avoid rate limits
                logger.info(f"Searching {media_type} for: {keyword}")

                if media_type == "videos":
                    results = await self._search_videos(keyword, results_per_keyword)
                else:
                    results = await self._search_photos(keyword, results_per_keyword)

                for result in results:
                    result["search_keyword"] = keyword

                all_results.extend(results)

            logger.info(f"Found {len(all_results)} {media_type} across {len(keywords)} keywords")

            return {
                "success": True,
                "results": all_results,
                "total_found": len(all_results),
                "keywords_searched": keywords[:10],
                "media_type": media_type
            }

        except Exception as e:
            logger.error(f"Error finding stock footage: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def _search_videos(self, query: str, per_page: int = 3) -> List[Dict[str, Any]]:
        """Search for videos on Pexels"""
        try:
            headers = {
                "Authorization": self.pexels_api_key
            }
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"  # Best for documentaries
            }

            response = requests.get(
                f"{self.pexels_videos_url}/search",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Pexels API error: {response.status_code}")
                return []

            data = response.json()
            videos = []

            for video in data.get("videos", []):
                # Get the best quality video file
                video_files = video.get("video_files", [])
                hd_file = self._get_best_quality_file(video_files)

                videos.append({
                    "id": video.get("id"),
                    "title": f"{query.title()} - {video.get('id')}",
                    "duration": video.get("duration", 0),
                    "width": video.get("width", 0),
                    "height": video.get("height", 0),
                    "thumbnail": video.get("image"),
                    "download_url": hd_file.get("link") if hd_file else None,
                    "quality": hd_file.get("quality") if hd_file else "unknown",
                    "video_url": video.get("url"),
                    "photographer": video.get("user", {}).get("name", "Unknown"),
                    "source": "Pexels"
                })

            return videos

        except Exception as e:
            logger.error(f"Error searching videos: {str(e)}")
            return []

    async def _search_photos(self, query: str, per_page: int = 3) -> List[Dict[str, Any]]:
        """Search for photos on Pexels"""
        try:
            headers = {
                "Authorization": self.pexels_api_key
            }
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }

            response = requests.get(
                f"{self.pexels_base_url}/search",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Pexels API error: {response.status_code}")
                return []

            data = response.json()
            photos = []

            for photo in data.get("photos", []):
                photos.append({
                    "id": photo.get("id"),
                    "title": f"{query.title()} - {photo.get('id')}",
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0),
                    "thumbnail": photo.get("src", {}).get("small"),
                    "preview_url": photo.get("src", {}).get("large"),
                    "download_url": photo.get("src", {}).get("original"),
                    "photographer": photo.get("photographer", "Unknown"),
                    "photo_url": photo.get("url"),
                    "source": "Pexels"
                })

            return photos

        except Exception as e:
            logger.error(f"Error searching photos: {str(e)}")
            return []

    def _get_best_quality_file(self, video_files: List[Dict]) -> Optional[Dict]:
        """Select the best quality video file (HD preferred)"""
        if not video_files:
            return None

        # Prefer HD quality
        hd_file = next((f for f in video_files if f.get("quality") == "hd"), None)
        if hd_file:
            return hd_file

        # Fallback to SD
        sd_file = next((f for f in video_files if f.get("quality") == "sd"), None)
        if sd_file:
            return sd_file

        # Return first available
        return video_files[0]

    def _get_mockup_results(self, keywords: List[str], media_type: str) -> Dict[str, Any]:
        """Return mockup results when API key is not available"""
        mockup_results = []

        for i, keyword in enumerate(keywords[:5]):
            mockup_results.append({
                "id": f"mockup_{i}",
                "title": f"{keyword.title()} - Stock {media_type.rstrip('s').title()}",
                "duration": 15 if media_type == "videos" else None,
                "width": 1920,
                "height": 1080,
                "thumbnail": f"https://via.placeholder.com/400x225?text={keyword.replace(' ', '+')}",
                "download_url": f"https://pexels.com/mockup/{keyword}",
                "quality": "hd",
                "photographer": "Stock Artist",
                "source": "Pexels (Mockup)",
                "search_keyword": keyword
            })

        return {
            "success": True,
            "results": mockup_results,
            "total_found": len(mockup_results),
            "keywords_searched": keywords[:5],
            "media_type": media_type,
            "note": "API key not configured - showing mockup data"
        }

    async def extract_broll_keywords(self, script: Dict[str, Any]) -> List[str]:
        """
        Extract B-roll keywords from script

        Args:
            script: Documentary script from Agent 13

        Returns:
            List of unique keywords for stock footage search
        """
        keywords = []

        if "chapters" in script:
            for chapter in script["chapters"]:
                # Extract from B-roll shots
                b_roll_shots = chapter.get("b_roll_shots", [])
                for shot in b_roll_shots:
                    if isinstance(shot, str):
                        # Clean and extract keywords
                        cleaned = shot.lower().strip('- ').strip()
                        keywords.append(cleaned)

        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)

        logger.info(f"Extracted {len(unique_keywords)} unique B-roll keywords from script")
        return unique_keywords[:20]  # Limit to 20 to avoid excessive API calls


# Singleton instance
stock_scout_service = StockScoutService()
