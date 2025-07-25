import json
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..auth import get_current_student, get_current_ta, get_current_teacher
from ..models import (
    User, QuizSubmissionSchema, AnswerKeyCreate, TaskStatus
)
from ..models.supabase_client import (
    insert, table, get_by_id, update_by_id, delete_by_id
)
from .ocr_processor import OCRProcessor
from .grading_system import GradingSystem

router = APIRouter()


@router.post("/upload_response", response_model=QuizSubmissionSchema)
async def upload_response(
    quiz_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_student),
) -> Any:
    """Upload PDF quiz response for OCR processing."""
    # Check if quiz exists
    quiz = get_by_id("quizzes", quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Check if file is a PDF
    if not file.content_type == "application/pdf" and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF document",
        )

    # Process submission
    submission, needs_review = await OCRProcessor.process_submission_pdf(
        file, quiz_id, current_user.id
    )

    saved = insert(
        "submissions",
        {
            "id": submission.id,
            "quiz_id": submission.quiz_id,
            "student_user_id": submission.student_id,
            "image_storage_url": submission.file_path,
            "ocr_text_content": submission.ocr_text,
            "ocr_confidence_score": submission.ocr_confidence,
            "status": submission.ocr_status,
        },
    )

    return saved


@router.post("/submit_answer_key")
async def submit_answer_key(
    answer_key_data: AnswerKeyCreate,
    current_user: User = Depends(get_current_ta),
) -> Dict[str, str]:
    """Submit correct answer key for a quiz."""
    # Check if quiz exists
    quiz = get_by_id("quizzes", answer_key_data.quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Process each answer key item
    for item in answer_key_data.answer_key:
        # Upsert answer key detail
        insert(
            "answer_key_details",
            {
                "id": str(uuid.uuid4()),
                "answer_key_id": answer_key_data.quiz_id,  # simplistic
                "question_id": item.question_id,
                "correct_text_or_choice": item.correct_answer,
                "keywords": item.keywords,
            },
        )

    return {"message": "Answer key submitted successfully"}


@router.post("/grade_submission/{submission_id}")
async def grade_submission(
    submission_id: str,
    current_user: User = Depends(get_current_ta),
) -> Dict[str, Any]:
    """Trigger AI grading for a specific student's quiz submission."""
    # Check if submission exists
    submission = get_by_id("submissions", submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    # Check if submission is ready for grading
    if submission["status"] != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission OCR processing is not complete",
        )

    # Grade submission (in a real app, this would be a background task)
    try:
        submission, student_answers = await GradingSystem.grade_submission(submission_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grading failed: {str(e)}",
        )

    return {
        "message": "Grading completed",
        "grade_status": submission.grade_status,
        "score": submission.score,
    }


@router.get("/quizzes", response_model=List[Dict[str, Any]])
async def get_quizzes(
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """Get all quizzes for the current user."""
    quizzes = (
        table("quizzes")
        .select("*")
        .eq("created_by_user_id", current_user.id)
        .execute()
        .data
    )
    result = []
    for quiz in quizzes:
        # Count submissions
        submission_count = (
            table("submissions")
            .select("id", count="exact")
            .eq("quiz_id", quiz["id"])
            .execute()
            .count
        )
        
        # Count graded submissions
        graded_count = (
            table("submissions")
            .select("id", count="exact")
            .eq("quiz_id", quiz["id"])
            .eq("status", TaskStatus.COMPLETED)
            .execute()
            .count
        )
        
        result.append({
            "id": quiz["id"],
            "title": quiz["title"],
            "description": quiz["description"],
            "created_at": quiz["created_at"],
            "difficulty": quiz["difficulty"],
            "submission_count": submission_count,
            "graded_count": graded_count,
        })
    
    return result


@router.get("/submissions/{quiz_id}", response_model=List[QuizSubmissionSchema])
async def get_submissions(
    quiz_id: str,
    current_user: User = Depends(get_current_ta),
) -> Any:
    """Get all submissions for a specific quiz."""
    # Check if quiz exists
    quiz = get_by_id("quizzes", quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    # Get submissions
    submissions = (
        table("submissions")
        .select("*")
        .eq("quiz_id", quiz_id)
        .execute()
        .data
    )
    
    return submissions 