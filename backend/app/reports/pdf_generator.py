import io
from typing import Dict, List, Optional, Tuple, Any

from fpdf import FPDF
import pandas as pd
from sqlalchemy.orm import Session

from ..models import (
    Quiz, QuizSubmission, StudentAnswer, Question, User, TaskStatus
)
from ..services import StorageClient


class ReportPDF(FPDF):
    """Custom PDF class for reports."""

    def header(self):
        """Add header to PDF."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AI-Powered Educational System", 0, 1, "C")
        self.ln(5)

    def footer(self):
        """Add footer to PDF."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


class PDFGenerator:
    """PDF generator for reports."""

    @staticmethod
    async def generate_student_report(
        submission_id: str, db: Session, user_id: str
    ) -> Tuple[str, str]:
        """Generate student report PDF."""
        # Get submission
        submission = db.query(QuizSubmission).filter(
            QuizSubmission.id == submission_id
        ).first()
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Get quiz
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
        if not quiz:
            raise ValueError(f"Quiz {submission.quiz_id} not found")
        
        # Get student
        student = db.query(User).filter(User.id == submission.student_id).first()
        if not student:
            raise ValueError(f"Student {submission.student_id} not found")
        
        # Get answers
        answers = db.query(StudentAnswer).filter(
            StudentAnswer.submission_id == submission_id
        ).all()
        
        # Create PDF
        pdf = ReportPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Quiz Report: {quiz.title}", 0, 1, "C")
        pdf.ln(5)
        
        # Add student info
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Student: {student.full_name or student.username}", 0, 1)
        pdf.cell(0, 10, f"Date: {submission.created_at.strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.cell(0, 10, f"Overall Score: {submission.score:.1f}%", 0, 1)
        pdf.ln(5)
        
        # Add answers and feedback
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Detailed Feedback", 0, 1)
        pdf.ln(5)
        
        for answer in answers:
            # Get question
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if not question:
                continue
            
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 10, f"Question: {question.text}")
            pdf.ln(2)
            
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 10, f"Your Answer: {answer.answer_text}")
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(0, 10, f"Score: {answer.score:.1f}%")
            pdf.ln(2)
            
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 10, f"Feedback: {answer.feedback}")
            pdf.ln(5)
        
        # Save PDF to memory
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Upload to storage
        file_path, file_url = await StorageClient.upload_generated_file(
            pdf_buffer.getvalue(),
            f"student_report_{submission_id}.pdf",
            user_id,
            StorageClient.BUCKET_REPORTS,
        )
        
        return file_path, file_url

    @staticmethod
    async def generate_class_summary(
        quiz_id: str, db: Session, user_id: str
    ) -> Tuple[str, str]:
        """Generate class summary PDF."""
        # Get quiz
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Get all submissions
        submissions = db.query(QuizSubmission).filter(
            QuizSubmission.quiz_id == quiz_id,
            QuizSubmission.grade_status == TaskStatus.COMPLETED,
        ).all()
        
        # Get all questions
        questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
        
        # Create PDF
        pdf = ReportPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Class Summary: {quiz.title}", 0, 1, "C")
        pdf.ln(5)
        
        # Add quiz info
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {quiz.created_at.strftime('%Y-%m-%d')}", 0, 1)
        pdf.cell(0, 10, f"Total Submissions: {len(submissions)}", 0, 1)
        
        # Calculate statistics
        if submissions:
            scores = [s.score for s in submissions if s.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0
            
            pdf.cell(0, 10, f"Average Score: {avg_score:.1f}%", 0, 1)
            pdf.cell(0, 10, f"Highest Score: {max_score:.1f}%", 0, 1)
            pdf.cell(0, 10, f"Lowest Score: {min_score:.1f}%", 0, 1)
        else:
            pdf.cell(0, 10, "No graded submissions available", 0, 1)
        
        pdf.ln(5)
        
        # Add question analysis
        if questions and submissions:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Question Analysis", 0, 1)
            pdf.ln(5)
            
            for question in questions:
                # Get all answers for this question
                answers = db.query(StudentAnswer).filter(
                    StudentAnswer.question_id == question.id
                ).all()
                
                if not answers:
                    continue
                
                # Calculate statistics
                scores = [a.score for a in answers if a.score is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                
                pdf.set_font("Arial", "B", 12)
                pdf.multi_cell(0, 10, f"Question: {question.text}")
                pdf.ln(2)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 10, f"Average Score: {avg_score:.1f}%", 0, 1)
                
                # Identify common issues (simplified approach)
                low_scores = [a for a in answers if a.score is not None and a.score < 50]
                if low_scores:
                    pdf.multi_cell(0, 10, f"Note: {len(low_scores)} students scored below 50% on this question.")
                
                pdf.ln(5)
        
        # Save PDF to memory
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Upload to storage
        file_path, file_url = await StorageClient.upload_generated_file(
            pdf_buffer.getvalue(),
            f"class_summary_{quiz_id}.pdf",
            user_id,
            StorageClient.BUCKET_REPORTS,
        )
        
        return file_path, file_url 