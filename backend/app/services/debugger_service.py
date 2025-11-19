"""
Debugger Service for Agent Testing & Diagnosis
Allows live testing of Gemini agents with custom configurations
"""

import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger("DebuggerService")


class DebuggerService:
    """Service for debugging and testing Gemini agents"""

    def __init__(self):
        """Initialize debugger service"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Debugger will be limited.")
        else:
            genai.configure(api_key=self.api_key)
            logger.info("Debugger service initialized")

    async def send_message(
        self,
        message: str,
        config: Dict[str, Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Gemini and get detailed response with logs

        Args:
            message: User message
            config: Agent configuration (model, temperature, system_instruction, etc.)
            chat_history: Previous messages in the conversation

        Returns:
            Dict with response text, raw response data, and logs
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY not configured",
                "response_text": "⚠️ Debugger requires GEMINI_API_KEY to be set",
                "raw_response": None,
                "logs": []
            }

        try:
            # Extract config
            model_name = config.get("model", "gemini-1.5-pro")
            system_instruction = config.get("system_instruction", "You are a helpful AI assistant.")
            temperature = config.get("temperature", 1.0)
            top_p = config.get("top_p", 0.95)
            top_k = config.get("top_k", 64)

            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=8192
            )

            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction
            )

            # Log request
            request_log = {
                "timestamp": datetime.now().isoformat(),
                "type": "request",
                "data": {
                    "message": message,
                    "model": model_name,
                    "config": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k
                    }
                }
            }

            # Start chat session if history exists
            if chat_history and len(chat_history) > 0:
                # Convert chat history to Gemini format
                history = []
                for msg in chat_history:
                    role = "model" if msg["role"] == "assistant" else "user"
                    history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

                chat = model.start_chat(history=history)
                response = chat.send_message(message)
            else:
                # Single message (no history)
                response = model.generate_content(message)

            # Extract response text
            response_text = response.text if hasattr(response, 'text') else str(response)

            # Log response
            response_log = {
                "timestamp": datetime.now().isoformat(),
                "type": "response",
                "data": {
                    "text": response_text,
                    "candidates_count": len(response.candidates) if hasattr(response, 'candidates') else 0,
                    "prompt_feedback": str(response.prompt_feedback) if hasattr(response, 'prompt_feedback') else None,
                    "usage_metadata": {
                        "prompt_token_count": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                        "candidates_token_count": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None,
                        "total_token_count": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None
                    } if hasattr(response, 'usage_metadata') else None
                }
            }

            # Build raw response structure for debugging
            raw_response = {
                "text": response_text,
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": part.text} for part in candidate.content.parts if hasattr(part, 'text')],
                            "role": candidate.content.role
                        },
                        "finish_reason": str(candidate.finish_reason) if hasattr(candidate, 'finish_reason') else None,
                        "safety_ratings": [
                            {
                                "category": str(rating.category),
                                "probability": str(rating.probability)
                            } for rating in candidate.safety_ratings
                        ] if hasattr(candidate, 'safety_ratings') else []
                    } for candidate in response.candidates
                ] if hasattr(response, 'candidates') else [],
                "usage_metadata": response_log["data"]["usage_metadata"]
            }

            logger.info(f"✅ Debugger message sent successfully. Tokens: {response_log['data']['usage_metadata']['total_token_count'] if response_log['data']['usage_metadata'] else 'N/A'}")

            return {
                "success": True,
                "response_text": response_text,
                "raw_response": raw_response,
                "logs": [request_log, response_log]
            }

        except Exception as e:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }

            logger.error(f"❌ Debugger error: {e}")

            return {
                "success": False,
                "error": str(e),
                "response_text": f"❌ Error: {str(e)}",
                "raw_response": None,
                "logs": [error_log]
            }

    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        return [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]

    def get_agent_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined agent configurations for testing"""
        return {
            "Agent 1 - Project Manager": {
                "system_instruction": "You are Agent 1: The Project Manager. Your role is to analyze music video concepts, generate genre variations, and manage viral trends. You think strategically and provide detailed creative direction.",
                "model": "gemini-1.5-pro",
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 64
            },
            "Agent 2 - Lyrics Writer": {
                "system_instruction": "You are Agent 2: The Lyrics Writer. You create compelling, emotionally resonant lyrics that tell stories. Your lyrics are poetic, catchy, and align with the music video's theme.",
                "model": "gemini-1.5-pro",
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 64
            },
            "Agent 3 - Music Style Analyzer": {
                "system_instruction": "You are Agent 3: The Music Style Analyzer. You analyze musical genres, identify key characteristics, and provide detailed style descriptions for music production.",
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64
            },
            "Agent 4 - Scene Planner": {
                "system_instruction": "You are Agent 4: The Scene Planner. You break down music videos into detailed scene-by-scene breakdowns with timestamps, moods, and visual descriptions.",
                "model": "gemini-1.5-pro",
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 64
            },
            "Agent 5 - Video Prompter (Veo)": {
                "system_instruction": "You are Agent 5: The Video Prompter for Google Veo. You create cinematic, narrative-driven video prompts that focus on storytelling and emotional impact. Keep prompts concise (50-100 words).",
                "model": "gemini-1.5-pro",
                "temperature": 0.75,
                "top_p": 0.95,
                "top_k": 64
            },
            "Agent 6 - Video Prompter (Runway)": {
                "system_instruction": "You are Agent 6: The Video Prompter for Runway Gen-4. You create modular, technical video prompts with precise camera movements and visual details. Keep prompts structured and specific.",
                "model": "gemini-1.5-pro",
                "temperature": 0.75,
                "top_p": 0.95,
                "top_k": 64
            },
            "Custom Agent": {
                "system_instruction": "You are a helpful and precise AI assistant. You always think step-by-step before answering.",
                "model": "gemini-1.5-pro",
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 64
            }
        }


# Singleton instance
debugger_service = DebuggerService()
