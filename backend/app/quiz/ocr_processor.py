import uuid
from typing import Dict, Tuple, Any

from fastapi import UploadFile

from ..models import QuizSubmission, TaskStatus
from ..services import OCRClient, StorageClient


class OCRProcessor:
    """OCR processor for PDF quiz responses."""

    # Confidence threshold for OCR results
    CONFIDENCE_THRESHOLD = 0.7

    @staticmethod
    async def process_submission_pdf(
        file: UploadFile, quiz_id: str, student_id: str
    ) -> Tuple[QuizSubmission, bool]:
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
        
        # Create submission record
        submission_id = str(uuid.uuid4())
        submission = QuizSubmission(
            id=submission_id,
            quiz_id=quiz_id,
            student_id=student_id,
            file_path=file_path,
            ocr_status=ocr_status,
            ocr_text=text,
            ocr_confidence=confidence,
            grade_status=TaskStatus.PENDING,
        )
        
        # Check if confidence is below threshold
        needs_review = confidence < OCRProcessor.CONFIDENCE_THRESHOLD
        
        return submission, needs_review 