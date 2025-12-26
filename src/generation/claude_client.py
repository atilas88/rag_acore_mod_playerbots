# src/generation/claude_client.py
"""
Client to interact with Claude's API
"""

import anthropic
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ClaudeClient:
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Claude"""

        try:
            logger.debug(f"🤖 Sending prompt to Claude (model: {self.model})")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response = message.content[0].text
            logger.debug(f"✅ Response received ({len(response)} characters)")

            return response

        except Exception as e:
            logger.error(f"❌ Error generating response: {str(e)}")
            raise
    
    def generate_response_streaming(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ):
        """Generate response in streaming mode"""

        try:
            logger.debug("🤖 Starting streaming with Claude")

            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            ) as stream:
                for text in stream.text_stream:
                    yield text

            logger.debug("✅ Streaming completed")

        except Exception as e:
            logger.error(f"❌ Streaming error: {str(e)}")
            raise
