from fastapi import APIRouter, File, UploadFile

from ..models import AnswerKey, GradeSubmissionRequest, QuizResponseUpload

router = APIRouter()


@router.post("/upload_response")
async def upload_response(quiz_id: str, student_id: str, image: UploadFile = File(...)):
    """Upload handwritten quiz image (stub)."""
    submission_id = "submission_123"
    return {"message": "Response uploaded and OCR initiated", "submission_id": submission_id}


@router.post("/submit_answer_key")
async def submit_answer_key(key: AnswerKey):
    """Submit answer key (stub)."""
    return {"message": "Answer key submitted successfully"}


@router.post("/grade_submission/{submission_id}")
async def grade_submission(submission_id: str):
    """Trigger AI grading (stub)."""
    return {"message": "Grading initiated", "grade_status": "processing"}
