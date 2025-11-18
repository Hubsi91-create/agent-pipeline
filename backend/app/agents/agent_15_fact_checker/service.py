"""
Agent 15: Fact Checker

Verifies factual claims in documentary scripts using AI and web search.
Uses Gemini with Google Search Grounding to validate statements.
"""

import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

from app.infrastructure.external_services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class FactCheckerService:
    """Agent 15: AI-powered fact verification for documentary scripts"""

    def __init__(self):
        self.gemini = gemini_service
        logger.info("Agent 15 (Fact Checker) initialized")

    async def verify_facts(
        self,
        script: Dict[str, Any],
        check_mode: str = "critical"
    ) -> Dict[str, Any]:
        """
        Verify factual claims in documentary script

        Args:
            script: Complete script from Agent 13
            check_mode: "critical" (numbers/dates/names) or "full" (all claims)

        Returns:
            {
                "success": bool,
                "fact_report": str,  # Markdown report
                "issues_found": int,
                "checks_performed": int,
                "critical_issues": List[Dict],
                "warnings": List[Dict],
                "verified_claims": List[Dict]
            }
        """
        try:
            # Extract text from script
            script_text = self._extract_script_text(script)

            # Extract factual claims
            claims = self._extract_claims(script_text, check_mode)

            logger.info(f"Extracted {len(claims)} claims for fact-checking")

            # Verify each claim
            results = []
            for claim in claims:
                verification = await self._verify_claim(claim)
                results.append(verification)

            # Generate fact report
            fact_report = self._generate_fact_report(results, script.get("title", "Documentary"))

            # Count issues
            critical_issues = [r for r in results if r["status"] == "false"]
            warnings = [r for r in results if r["status"] == "uncertain"]
            verified = [r for r in results if r["status"] == "verified"]

            return {
                "success": True,
                "fact_report": fact_report,
                "issues_found": len(critical_issues),
                "checks_performed": len(results),
                "critical_issues": critical_issues,
                "warnings": warnings,
                "verified_claims": verified,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error during fact-checking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fact_report": f"⚠️ **Error during fact-checking:** {str(e)}"
            }

    def _extract_script_text(self, script: Dict[str, Any]) -> str:
        """Extract all narration text from script"""
        text_parts = []

        if "chapters" in script:
            for chapter in script["chapters"]:
                narration = chapter.get("narration", "")
                if narration:
                    text_parts.append(narration)

        return "\n\n".join(text_parts)

    def _extract_claims(self, text: str, check_mode: str) -> List[str]:
        """
        Extract factual claims from text

        Critical mode: Focus on numbers, dates, names, statistics
        Full mode: Extract all factual statements
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        claims = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if check_mode == "critical":
                # Look for sentences with numbers, dates, or specific names
                if self._contains_verifiable_fact(sentence):
                    claims.append(sentence)
            else:
                # Full mode: check all statements
                if len(sentence.split()) > 5:  # Only meaningful sentences
                    claims.append(sentence)

        return claims[:20]  # Limit to 20 claims to avoid excessive API calls

    def _contains_verifiable_fact(self, sentence: str) -> bool:
        """Check if sentence contains verifiable facts (numbers, dates, etc.)"""
        patterns = [
            r'\d{4}',  # Years
            r'\d+%',  # Percentages
            r'\d+\s*(million|billion|thousand)',  # Large numbers
            r'(January|February|March|April|May|June|July|August|September|October|November|December)',  # Dates
            r'\$\d+',  # Money
            r'\d+\s*(km|miles|meters|feet)',  # Measurements
        ]

        for pattern in patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True

        return False

    async def _verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Verify a single claim using Gemini with Google Search

        Returns:
            {
                "claim": str,
                "status": "verified" | "false" | "uncertain",
                "explanation": str,
                "sources": List[str]
            }
        """
        try:
            # Build verification prompt
            prompt = f"""You are a fact-checker for a documentary. Verify the following claim:

CLAIM: "{claim}"

Task:
1. Use your knowledge and available search to verify this claim
2. Determine if it is TRUE, FALSE, or UNCERTAIN
3. Provide a brief explanation
4. If possible, cite sources

Response format:
STATUS: [VERIFIED/FALSE/UNCERTAIN]
EXPLANATION: [Brief explanation]
SOURCES: [URLs or references if available]
"""

            # Call Gemini (with Google Search grounding if available)
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,  # Low temperature for factual accuracy
                max_tokens=500
            )

            result = response.get("text", "")

            # Parse response
            status = self._parse_status(result)
            explanation = self._parse_explanation(result)
            sources = self._parse_sources(result)

            return {
                "claim": claim,
                "status": status,
                "explanation": explanation,
                "sources": sources,
                "raw_response": result
            }

        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "claim": claim,
                "status": "uncertain",
                "explanation": f"Error during verification: {str(e)}",
                "sources": []
            }

    def _parse_status(self, response: str) -> str:
        """Parse verification status from AI response"""
        response_lower = response.lower()

        if "status: verified" in response_lower or "status: true" in response_lower:
            return "verified"
        elif "status: false" in response_lower:
            return "false"
        else:
            return "uncertain"

    def _parse_explanation(self, response: str) -> str:
        """Extract explanation from AI response"""
        # Look for EXPLANATION: section
        match = re.search(r'EXPLANATION:\s*(.+?)(?=SOURCES:|$)', response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: return first paragraph
        lines = response.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('STATUS:') and not line.startswith('SOURCES:'):
                return line.strip()

        return response[:200]

    def _parse_sources(self, response: str) -> List[str]:
        """Extract source URLs from AI response"""
        # Look for SOURCES: section
        match = re.search(r'SOURCES:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
        if match:
            sources_text = match.group(1).strip()
            # Extract URLs
            urls = re.findall(r'https?://[^\s]+', sources_text)
            return urls

        return []

    def _generate_fact_report(
        self,
        results: List[Dict[str, Any]],
        doc_title: str
    ) -> str:
        """Generate markdown fact-checking report"""
        report_lines = [
            f"# 📋 Fact-Check Report: {doc_title}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Claims Checked:** {len(results)}",
            ""
        ]

        # Summary
        verified_count = len([r for r in results if r["status"] == "verified"])
        false_count = len([r for r in results if r["status"] == "false"])
        uncertain_count = len([r for r in results if r["status"] == "uncertain"])

        report_lines.append("## 📊 Summary")
        report_lines.append(f"- ✅ **Verified:** {verified_count}")
        report_lines.append(f"- ❌ **False/Misleading:** {false_count}")
        report_lines.append(f"- ⚠️ **Uncertain:** {uncertain_count}")
        report_lines.append("")

        # Critical Issues
        if false_count > 0:
            report_lines.append("## 🚨 Critical Issues (MUST FIX)")
            report_lines.append("")
            for result in results:
                if result["status"] == "false":
                    report_lines.append(f"### ❌ {result['claim']}")
                    report_lines.append(f"**Issue:** {result['explanation']}")
                    if result.get("sources"):
                        report_lines.append(f"**Sources:** {', '.join(result['sources'])}")
                    report_lines.append("")

        # Warnings
        if uncertain_count > 0:
            report_lines.append("## ⚠️ Warnings (Review Recommended)")
            report_lines.append("")
            for result in results:
                if result["status"] == "uncertain":
                    report_lines.append(f"### ⚠️ {result['claim']}")
                    report_lines.append(f"**Note:** {result['explanation']}")
                    report_lines.append("")

        # Verified Claims
        if verified_count > 0:
            report_lines.append("## ✅ Verified Claims")
            report_lines.append("")
            for result in results:
                if result["status"] == "verified":
                    report_lines.append(f"- ✅ {result['claim']}")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("**Note:** This is an AI-assisted fact-check. Always verify critical claims with primary sources.")

        return "\n".join(report_lines)


# Singleton instance
fact_checker_service = FactCheckerService()
