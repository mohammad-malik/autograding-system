from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserRole(str, Enum):
    """User role enum."""
    TEACHER = "teacher"
    TA = "ta"
    STUDENT = "student"


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserInDB(UserBase):
    """User model in database."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class User(UserBase):
    """User model returned to client."""
    id: str
    created_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str
    user_role: UserRole


class TokenPayload(BaseModel):
    """Token payload model."""
    sub: str
    role: UserRole
    exp: int


class TextbookBase(BaseModel):
    """Base textbook model."""
    title: str
    author: Optional[str] = None
    description: Optional[str] = None


class TextbookCreate(TextbookBase):
    """Textbook creation model."""
    pass


class Textbook(TextbookBase):
    """Textbook model returned to client."""
    id: str
    file_path: str
    created_by: str
    created_at: datetime
    indexed: bool = False

    class Config:
        """Pydantic config."""
        orm_mode = True


class QuestionType(str, Enum):
    """Question type enum."""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"


class Difficulty(str, Enum):
    """Difficulty enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SlideGenerationRequest(BaseModel):
    """Slide generation request model."""
    prompt: str
    book_id: str
    num_slides: int = Field(ge=1, le=50)


class QuizGenerationRequest(BaseModel):
    """Quiz generation request model."""
    prompt: str
    book_id: str
    question_types: List[QuestionType]
    difficulty: Difficulty


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    message: str
    status: TaskStatus
    download_url: Optional[HttpUrl] = None


class QuizSubmissionBase(BaseModel):
    """Base quiz submission model."""
    quiz_id: str
    student_id: str


class QuizSubmissionCreate(QuizSubmissionBase):
    """Quiz submission creation model."""
    pass


class QuizSubmission(QuizSubmissionBase):
    """Quiz submission model returned to client."""
    id: str
    file_path: str
    ocr_status: TaskStatus
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    grade_status: TaskStatus = TaskStatus.PENDING
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class AnswerKeyItem(BaseModel):
    """Answer key item model."""
    question_id: str
    correct_answer: str
    keywords: Optional[List[str]] = None


class AnswerKeyCreate(BaseModel):
    """Answer key creation model."""
    quiz_id: str
    answer_key: List[AnswerKeyItem]


class ReportResponse(BaseModel):
    """Report response model."""
    message: str
    download_pdf_url: HttpUrl


class ClassSummary(BaseModel):
    """Class summary model."""
    quiz_name: str
    avg_score: float
    common_mistakes: List[str]
    performance_trends: Dict[str, Any]
    download_pdf_url: HttpUrl 