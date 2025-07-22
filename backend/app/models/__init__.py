from .database import Base, User, Textbook, Quiz, Question, AnswerKey, QuizSubmission, StudentAnswer
from .schemas import (
    UserRole, UserBase, UserCreate, UserInDB, User as UserSchema, Token, TokenPayload,
    TextbookBase, TextbookCreate, Textbook as TextbookSchema,
    QuestionType, Difficulty, SlideGenerationRequest, QuizGenerationRequest,
    TaskStatus, TaskResponse, QuizSubmissionBase, QuizSubmissionCreate,
    QuizSubmission as QuizSubmissionSchema, AnswerKeyItem, AnswerKeyCreate,
    ReportResponse, ClassSummary
)
from .database_utils import get_db, init_db, supabase 