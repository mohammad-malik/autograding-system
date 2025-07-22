from fastapi import APIRouter

from ..models import ReportResponse

router = APIRouter()


@router.get("/student/{submission_id}", response_model=ReportResponse)
async def get_student_report(submission_id: str):
    """Return a fake student report."""
    return ReportResponse(student_name="Jane Doe", score=95.0, feedback="Great work!", download_pdf_url=None)


@router.get("/class_summary/{quiz_id}")
async def class_summary(quiz_id: str):
    """Return fake class analytics."""
    return {
        "quiz_name": "Sample Quiz",
        "avg_score": 90.0,
        "common_mistakes": [],
        "performance_trends": {},
        "download_pdf_url": None,
    }
