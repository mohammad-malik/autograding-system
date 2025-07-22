import json
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..auth import get_current_student, get_current_ta, get_current_teacher
from ..models import (
    User, Quiz, QuizSubmission, QuizSubmissionCreate, QuizSubmissionSchema,
    AnswerKeyCreate, AnswerKey, Question, TaskStatus
)
from ..models.database_utils import get_db
from .ocr_processor import OCRProcessor
from .grading_system import GradingSystem

router = APIRouter()


@router.post("/upload_response", response_model=QuizSubmissionSchema)
async def upload_response(
    quiz_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> Any:
    """Upload PDF quiz response for OCR processing."""
    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
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

    # Save submission to database
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission


@router.post("/submit_answer_key")
async def submit_answer_key(
    answer_key_data: AnswerKeyCreate,
    current_user: User = Depends(get_current_ta),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Submit correct answer key for a quiz."""
    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == answer_key_data.quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Process each answer key item
    for item in answer_key_data.answer_key:
        # Check if question exists
        question = db.query(Question).filter(Question.id == item.question_id).first()
        if not question:
            continue

        # Check if answer key already exists
        existing_key = db.query(AnswerKey).filter(
            AnswerKey.question_id == item.question_id
        ).first()

        if existing_key:
            # Update existing answer key
            existing_key.correct_answer = item.correct_answer
            existing_key.keywords = json.dumps(item.keywords) if item.keywords else None
        else:
            # Create new answer key
            answer_key = AnswerKey(
                id=str(uuid.uuid4()),
                question_id=item.question_id,
                correct_answer=item.correct_answer,
                keywords=json.dumps(item.keywords) if item.keywords else None,
            )
            db.add(answer_key)

    # Commit changes
    db.commit()

    return {"message": "Answer key submitted successfully"}


@router.post("/grade_submission/{submission_id}")
async def grade_submission(
    submission_id: str,
    current_user: User = Depends(get_current_ta),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Trigger AI grading for a specific student's quiz submission."""
    # Check if submission exists
    submission = db.query(QuizSubmission).filter(
        QuizSubmission.id == submission_id
    ).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    # Check if submission is ready for grading
    if submission.ocr_status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission OCR processing is not complete",
        )

    # Grade submission (in a real app, this would be a background task)
    try:
        submission, student_answers = await GradingSystem.grade_submission(
            submission_id, db
        )
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
    db: Session = Depends(get_db),
) -> Any:
    """Get all quizzes for the current user."""
    quizzes = db.query(Quiz).filter(Quiz.created_by == current_user.id).all()
    result = []
    for quiz in quizzes:
        # Count submissions
        submission_count = db.query(QuizSubmission).filter(
            QuizSubmission.quiz_id == quiz.id
        ).count()
        
        # Count graded submissions
        graded_count = db.query(QuizSubmission).filter(
            QuizSubmission.quiz_id == quiz.id,
            QuizSubmission.grade_status == TaskStatus.COMPLETED,
        ).count()
        
        result.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "created_at": quiz.created_at,
            "difficulty": quiz.difficulty,
            "submission_count": submission_count,
            "graded_count": graded_count,
        })
    
    return result


@router.get("/submissions/{quiz_id}", response_model=List[QuizSubmissionSchema])
async def get_submissions(
    quiz_id: str,
    current_user: User = Depends(get_current_ta),
    db: Session = Depends(get_db),
) -> Any:
    """Get all submissions for a specific quiz."""
    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    # Get submissions
    submissions = db.query(QuizSubmission).filter(
        QuizSubmission.quiz_id == quiz_id
    ).all()
    
    return submissions 