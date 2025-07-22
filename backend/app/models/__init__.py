"""Pydantic models used across the application."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class TextbookUploadResponse(BaseModel):
    message: str
    book_id: str


class SlideGenerationRequest(BaseModel):
    prompt: str
    book_id: str
    num_slides: int


class SlideGenerationResponse(BaseModel):
    message: str
    task_id: str
    download_url: Optional[str] = None


class QuizGenerationRequest(BaseModel):
    prompt: str
    book_id: str
    question_types: List[str]
    difficulty: str


class QuizGenerationResponse(BaseModel):
    message: str
    task_id: str
    download_url: Optional[str] = None


class QuizResponseUpload(BaseModel):
    quiz_id: str
    student_id: str


class AnswerKeyItem(BaseModel):
    question_id: str
    correct_answer: str
    keywords: List[str] = []


class AnswerKey(BaseModel):
    quiz_id: str
    answer_key: List[AnswerKeyItem]


class GradeSubmissionRequest(BaseModel):
    submission_id: str
    quiz_id: str


class ReportResponse(BaseModel):
    student_name: str
    score: float
    feedback: str
    download_pdf_url: Optional[str] = None
