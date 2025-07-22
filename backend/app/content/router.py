from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..models import (
    QuizGenerationRequest,
    QuizGenerationResponse,
    SlideGenerationRequest,
    SlideGenerationResponse,
    TextbookUploadResponse,
)

router = APIRouter()


@router.post("/upload_textbook", response_model=TextbookUploadResponse)
async def upload_textbook(file: UploadFile = File(...)):
    """Upload textbook PDF and return a fake book ID."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    book_id = "book_123"
    return TextbookUploadResponse(message="Textbook processed and indexed successfully", book_id=book_id)


@router.post("/generate_slides", response_model=SlideGenerationResponse)
async def generate_slides(request: SlideGenerationRequest):
    """Generate slides from a prompt (stub)."""
    task_id = "task_slides_123"
    return SlideGenerationResponse(message="Slide generation initiated", task_id=task_id)


@router.post("/generate_quiz", response_model=QuizGenerationResponse)
async def generate_quiz(request: QuizGenerationRequest):
    """Generate quiz from a prompt (stub)."""
    task_id = "task_quiz_123"
    return QuizGenerationResponse(message="Quiz generation initiated", task_id=task_id)
