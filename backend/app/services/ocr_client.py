import json
from typing import Dict, Tuple, Optional, Any

from mistralai import Mistral, DocumentURLChunk
from pathlib import Path
import tempfile

from ..config import get_settings


class OCRClient:
    """Client for OCR services using MistralAI's OCR for PDF documents."""

    @staticmethod
    async def process_pdf(pdf_content: bytes) -> Tuple[str, float]:
        """
        Process PDF document using MistralAI's OCR service.
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Tuple of (extracted_text, confidence)
        """
        # Initialize Mistral client
        api_key = get_settings().mistralocr_api_key
        if not api_key:
            raise ValueError("MistralOCR API key not set")
        
        client = Mistral(api_key=api_key)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload PDF file to Mistral's OCR service
            pdf_file = Path(temp_file_path)
            uploaded_file = client.files.upload(
                file={
                    "file_name": "document",
                    "content": pdf_file.read_bytes(),
                },
                purpose="ocr",
            )
            
            # Get URL for the uploaded file
            signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            
            # Process PDF with OCR
            pdf_response = client.ocr.process(
                document=DocumentURLChunk(document_url=signed_url.url),
                model="mistral-ocr-latest",
            )
            
            # Extract text from all pages
            extracted_text = ""
            for page in pdf_response.pages:
                extracted_text += page.text + "\n\n"
            
            # For simplicity, we're using a fixed confidence value
            # In a real application, you might want to calculate this based on OCR results
            confidence = 0.95
            
            return extracted_text.strip(), confidence
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
        finally:
            # Clean up the temporary file
            Path(temp_file_path).unlink(missing_ok=True) 