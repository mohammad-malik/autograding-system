from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_student, get_current_ta, get_current_teacher
from ..models import User, QuizSubmission, Quiz, ClassSummary, ReportResponse
from ..models.database_utils import get_db
from .pdf_generator import PDFGenerator

router = APIRouter()


@router.get("/student/{submission_id}", response_model=ReportResponse)
async def get_student_report(
    submission_id: str,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
) -> Any:
    """Get student report for a specific submission."""
    # Check if submission exists
    submission = db.query(QuizSubmission).filter(
        QuizSubmission.id == submission_id
    ).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )
    
    # Check if user has permission
    if current_user.role == "student" and current_user.id != submission.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Generate report
    try:
        _, file_url = await PDFGenerator.generate_student_report(
            submission_id, db, current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )
    
    return {
        "message": "Student report generated successfully",
        "download_pdf_url": file_url,
    }


@router.get("/class_summary/{quiz_id}", response_model=ClassSummary)
async def get_class_summary(
    quiz_id: str,
    current_user: User = Depends(get_current_ta),
    db: Session = Depends(get_db),
) -> Any:
    """Get class summary for a specific quiz."""
    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    # Generate report
    try:
        _, file_url = await PDFGenerator.generate_class_summary(
            quiz_id, db, current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )
    
    # Get submissions
    submissions = db.query(QuizSubmission).filter(
        QuizSubmission.quiz_id == quiz_id
    ).all()
    
    # Calculate statistics
    scores = [s.score for s in submissions if s.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Simplified common mistakes (in a real app, this would be more sophisticated)
    common_mistakes = ["Incomplete answers", "Misunderstanding of key concepts"]
    
    # Simplified performance trends
    performance_trends = {
        "score_distribution": {
            "0-25": len([s for s in scores if s < 25]),
            "25-50": len([s for s in scores if 25 <= s < 50]),
            "50-75": len([s for s in scores if 50 <= s < 75]),
            "75-100": len([s for s in scores if s >= 75]),
        }
    }
    
    return {
        "quiz_name": quiz.title,
        "avg_score": avg_score,
        "common_mistakes": common_mistakes,
        "performance_trends": performance_trends,
        "download_pdf_url": file_url,
    } 