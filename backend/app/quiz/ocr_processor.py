import uuid
from typing import Tuple

from fastapi import UploadFile

from ..models import TaskStatus
from types import SimpleNamespace
from ..services import OCRClient, StorageClient


class OCRProcessor:
    """OCR processor for PDF quiz responses."""

    # Confidence threshold for OCR results
    CONFIDENCE_THRESHOLD = 0.7

    @staticmethod
    async def process_submission_pdf(
        file: UploadFile, quiz_id: str, student_id: str
    ) -> Tuple[dict, bool]:
        """Process submission PDF."""
        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are accepted")
            
        # Read file content
        file_content = await file.read()
        
        # Upload file to storage
        file_path, _ = await StorageClient.upload_quiz_pdf(
            file_content, file.filename, student_id, quiz_id
        )
        
        # Perform OCR
        try:
            text, confidence = await OCRClient.process_pdf(file_content)
            ocr_status = TaskStatus.COMPLETED
        except Exception as e:
            text = f"OCR failed: {str(e)}"
            confidence = 0.0
            ocr_status = TaskStatus.FAILED
        
        submission_id = str(uuid.uuid4())
        submission = {
            "id": submission_id,
            "quiz_id": quiz_id,
            "student_user_id": student_id,
            "image_storage_url": file_path,
            "ocr_text_content": text,
            "ocr_confidence_score": confidence,
            "status": ocr_status,
        }
        
        # Check if confidence is below threshold
        needs_review = confidence < OCRProcessor.CONFIDENCE_THRESHOLD
        
        return submission, needs_review 