import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..auth import get_current_teacher
from ..models import (
    User, Textbook, TextbookCreate, TextbookSchema, SlideGenerationRequest,
    QuizGenerationRequest, TaskResponse, TaskStatus, Quiz, QuestionType, Difficulty
)
from ..models.database_utils import get_db
from .pdf_processor import PDFProcessor
from .content_generator import ContentGenerator

router = APIRouter()


@router.post("/upload_textbook", response_model=TextbookSchema)
async def upload_textbook(
    title: str = Form(...),
    author: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Any:
    """Upload textbook PDF for processing and indexing."""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Create textbook data
    textbook_data = TextbookCreate(
        title=title,
        author=author,
        description=description,
    )

    # Process PDF
    textbook, chunk_ids = await PDFProcessor.process_pdf(
        file, textbook_data, current_user.id
    )

    # Save textbook to database
    db.add(textbook)
    db.commit()
    db.refresh(textbook)

    return textbook


@router.post("/generate_slides", response_model=TaskResponse)
async def generate_slides(
    request: SlideGenerationRequest,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Any:
    """Generate PowerPoint slides from textbook content."""
    # Check if textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == request.book_id).first()
    if not textbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Textbook not found",
        )

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Generate slides (in a real app, this would be a background task)
    file_path, file_url, task_status = await ContentGenerator.generate_slides(
        request.prompt, request.book_id, request.num_slides, current_user.id
    )

    return {
        "task_id": task_id,
        "message": "Slide generation completed",
        "status": task_status,
        "download_url": file_url,
    }


@router.post("/generate_quiz", response_model=TaskResponse)
async def generate_quiz(
    request: QuizGenerationRequest,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Any:
    """Generate quiz document from textbook content."""
    # Check if textbook exists
    textbook = db.query(Textbook).filter(Textbook.id == request.book_id).first()
    if not textbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Textbook not found",
        )

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Generate quiz (in a real app, this would be a background task)
    quiz, file_url, task_status = await ContentGenerator.generate_quiz(
        request.prompt,
        request.book_id,
        [qt.value for qt in request.question_types],
        request.difficulty.value,
        current_user.id,
    )

    # Save quiz to database
    db.add(quiz)
    db.commit()

    return {
        "task_id": task_id,
        "message": "Quiz generation completed",
        "status": task_status,
        "download_url": file_url,
    }


@router.get("/textbooks", response_model=List[TextbookSchema])
async def get_textbooks(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Any:
    """Get all textbooks for the current user."""
    textbooks = db.query(Textbook).filter(Textbook.created_by == current_user.id).all()
    return textbooks 