"""Stub for OCR service."""


class OCRClient:
    """Simplified OCR client."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def extract_text(self, image_bytes: bytes) -> str:
        """Return dummy text from image."""
        return "dummy ocr text"
