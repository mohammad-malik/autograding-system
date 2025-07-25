import io
from typing import Dict, List, Optional, Tuple, Any

from fpdf import FPDF

from ..services import StorageClient
from ..models import TaskStatus
from ..models.supabase_client import table, get_by_id


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
        submission_id: str, user_id: str
    ) -> Tuple[str, str]:
        """Generate student report PDF."""
        # Get submission
        submission = get_by_id("submissions", submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Get quiz
        quiz = get_by_id("quizzes", submission["quiz_id"])
        if not quiz:
            raise ValueError(f"Quiz {submission.quiz_id} not found")
        
        # Get student
        student = get_by_id("profiles", submission["student_user_id"])
        if not student:
            raise ValueError(f"Student {submission.student_id} not found")
        
        # Get answers
        answers = (
            table("grades")
            .select("*")
            .eq("submission_id", submission_id)
            .execute()
            .data
        )
        
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
            question = get_by_id("quiz_questions", answer["question_id"])
            if not question:
                continue
            
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 10, f"Question: {question['question_text']}")
            pdf.ln(2)
            
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 10, f"Your Answer: {answer['answer_text'] if 'answer_text' in answer else ''}")
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(0, 10, f"Score: {answer['assigned_score']:.1f}%")
            pdf.ln(2)
            
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 10, f"Feedback: {answer.get('llm_feedback', '')}")
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
        quiz_id: str, user_id: str
    ) -> Tuple[str, str]:
        """Generate class summary PDF."""
        # Get quiz
        quiz = get_by_id("quizzes", quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Get all submissions
        submissions = (
            table("submissions")
            .select("*")
            .eq("quiz_id", quiz_id)
            .eq("status", TaskStatus.COMPLETED)
            .execute()
            .data
        )
        
        # Get all questions
        questions = (
            table("quiz_questions")
            .select("*")
            .eq("quiz_id", quiz_id)
            .execute()
            .data
        )
        
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
                answers = (
                    table("grades")
                    .select("*")
                    .eq("question_id", question["id"])
                    .execute()
                    .data
                )
                
                if not answers:
                    continue
                
                # Calculate statistics
                scores = [a["assigned_score"] for a in answers if a["assigned_score"] is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                
                pdf.set_font("Arial", "B", 12)
                pdf.multi_cell(0, 10, f"Question: {question['question_text']}")
                pdf.ln(2)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 10, f"Average Score: {avg_score:.1f}%", 0, 1)
                
                # Identify common issues (simplified approach)
                low_scores = [a for a in answers if a["assigned_score"] is not None and a["assigned_score"] < 50]
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