"""Wrapper around OpenAI API for text generation."""
from typing import List


class OpenAIClient:
    """Simplified OpenAI client stub."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_text(self, prompt: str, max_tokens: int = 256) -> str:
        """Return dummy generated text for now."""
        # In production, call OpenAI API here.
        return f"Generated content for: {prompt[:20]}..."


