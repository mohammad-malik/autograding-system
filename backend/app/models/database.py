from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .schemas import UserRole, TaskStatus, QuestionType, Difficulty

Base = declarative_base()


class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    textbooks = relationship("Textbook", back_populates="creator")
    quizzes = relationship("Quiz", back_populates="creator")
    submissions = relationship("QuizSubmission", back_populates="student")


class Textbook(Base):
    """Textbook database model."""
    __tablename__ = "textbooks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    indexed = Column(Boolean, default=False)

    creator = relationship("User", back_populates="textbooks")
    quizzes = relationship("Quiz", back_populates="textbook")


class Quiz(Base):
    """Quiz database model."""
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)
    textbook_id = Column(String, ForeignKey("textbooks.id"))
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    difficulty = Column(Enum(Difficulty), default=Difficulty.MEDIUM)

    creator = relationship("User", back_populates="quizzes")
    textbook = relationship("Textbook", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    submissions = relationship("QuizSubmission", back_populates="quiz")


class Question(Base):
    """Question database model."""
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)
    quiz_id = Column(String, ForeignKey("quizzes.id"))
    text = Column(Text)
    question_type = Column(Enum(QuestionType))
    options = Column(Text, nullable=True)  # JSON string for multiple choice
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="questions")
    answer_key = relationship("AnswerKey", back_populates="question", uselist=False)


class AnswerKey(Base):
    """Answer key database model."""
    __tablename__ = "answer_keys"

    id = Column(String, primary_key=True, index=True)
    question_id = Column(String, ForeignKey("questions.id"), unique=True)
    correct_answer = Column(Text)
    keywords = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = relationship("Question", back_populates="answer_key")


class QuizSubmission(Base):
    """Quiz submission database model."""
    __tablename__ = "quiz_submissions"

    id = Column(String, primary_key=True, index=True)
    quiz_id = Column(String, ForeignKey("quizzes.id"))
    student_id = Column(String, ForeignKey("users.id"))
    file_path = Column(String)
    ocr_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    grade_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    answers = relationship("StudentAnswer", back_populates="submission")


class StudentAnswer(Base):
    """Student answer database model."""
    __tablename__ = "student_answers"

    id = Column(String, primary_key=True, index=True)
    submission_id = Column(String, ForeignKey("quiz_submissions.id"))
    question_id = Column(String, ForeignKey("questions.id"))
    answer_text = Column(Text)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("QuizSubmission", back_populates="answers")
    question = relationship("Question") 