import asyncio
import os
import logging
import sys
from dotenv import load_dotenv
from app.agents.agent_1_project_manager.service import agent1_service

# Load env vars
load_dotenv()

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def test_variations():
    print("Testing generate_genre_variations...")
    try:
        variations = await agent1_service.generate_genre_variations("Reggaeton", 5)
        print(f"Success! Got {len(variations)} variations.")
        print(variations)
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_variations())
