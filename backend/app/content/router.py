import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..auth import get_current_teacher
from ..models import (
    User, TextbookCreate, TextbookSchema, SlideGenerationRequest,
    QuizGenerationRequest, TaskResponse, TaskStatus, Difficulty
)
from ..models.supabase_client import insert, table, get_by_id
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

    # Save textbook to Supabase
    saved = insert(
        "books",
        {
            "id": textbook.id,
            "title": textbook.title,
            "author": textbook.author,
            "description": textbook.description,
            "file_path": textbook.file_path,
            "uploaded_by_user_id": current_user.id,
            "status": "pending_processing",
        },
    )

    return saved


@router.post("/generate_slides", response_model=TaskResponse)
async def generate_slides(
    request: SlideGenerationRequest,
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """Generate PowerPoint slides from textbook content."""
    # Check if textbook exists
    textbook = get_by_id("books", request.book_id)
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
) -> Any:
    """Generate quiz document from textbook content."""
    # Check if textbook exists
    textbook = get_by_id("books", request.book_id)
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

    insert(
        "quizzes",
        {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "file_path": quiz.file_path,
            "textbook_id": quiz.textbook_id,
            "created_by_user_id": current_user.id,
            "difficulty": quiz.difficulty,
            "status": "draft",
        },
    )

    return {
        "task_id": task_id,
        "message": "Quiz generation completed",
        "status": task_status,
        "download_url": file_url,
    }


@router.get("/textbooks", response_model=List[TextbookSchema])
async def get_textbooks(
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """Get all textbooks for the current user."""
    textbooks = (
        table("books")
        .select("*")
        .eq("uploaded_by_user_id", current_user.id)
        .execute()
        .data
    )
    return textbooks 