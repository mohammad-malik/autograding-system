import json
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy.orm import Session

from ..models import (
    QuizSubmission, Question, AnswerKey, StudentAnswer, TaskStatus
)
from ..services import LLMClient


class GradingSystem:
    """Grading system for quiz submissions."""

    @staticmethod
    async def grade_submission(
        submission_id: str, db: Session
    ) -> Tuple[QuizSubmission, List[StudentAnswer]]:
        """Grade quiz submission."""
        # Get submission
        submission = db.query(QuizSubmission).filter(
            QuizSubmission.id == submission_id
        ).first()
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Check if OCR was successful
        if submission.ocr_status != TaskStatus.COMPLETED:
            submission.grade_status = TaskStatus.FAILED
            db.commit()
            return submission, []
        
        # Get quiz questions
        questions = db.query(Question).filter(
            Question.quiz_id == submission.quiz_id
        ).all()
        if not questions:
            submission.grade_status = TaskStatus.FAILED
            submission.feedback = "No questions found for this quiz"
            db.commit()
            return submission, []
        
        # Parse OCR text to extract answers
        # This is a simplified approach - in a real system, you would need more robust parsing
        ocr_lines = submission.ocr_text.split("\n")
        answers = {}
        current_question = None
        current_answer = []
        
        for line in ocr_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a question number
            if line[0].isdigit() and "." in line[:3]:
                # Save previous answer if any
                if current_question is not None and current_answer:
                    answers[current_question] = " ".join(current_answer)
                    current_answer = []
                
                # Extract question number
                try:
                    question_num = int(line.split(".")[0])
                    current_question = question_num
                except:
                    current_question = None
            elif current_question is not None:
                current_answer.append(line)
        
        # Save last answer if any
        if current_question is not None and current_answer:
            answers[current_question] = " ".join(current_answer)
        
        # Grade each answer
        student_answers = []
        total_score = 0.0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            # Get answer key
            answer_key = db.query(AnswerKey).filter(
                AnswerKey.question_id == question.id
            ).first()
            if not answer_key:
                continue
            
            # Get student answer
            student_answer_text = answers.get(i + 1, "")
            
            # Grade answer
            keywords = json.loads(answer_key.keywords) if answer_key.keywords else None
            grade_result = await LLMClient.grade_submission(
                student_answer_text,
                question.text,
                answer_key.correct_answer,
                keywords,
            )
            
            # Create student answer record
            student_answer = StudentAnswer(
                id=f"{submission_id}_{question.id}",
                submission_id=submission_id,
                question_id=question.id,
                answer_text=student_answer_text,
                score=grade_result["score"],
                feedback=grade_result["feedback"],
            )
            student_answers.append(student_answer)
            db.add(student_answer)
            
            # Add to total score
            total_score += grade_result["score"]
        
        # Calculate average score
        avg_score = total_score / total_questions if total_questions > 0 else 0
        
        # Update submission
        submission.score = avg_score
        submission.grade_status = TaskStatus.COMPLETED
        submission.feedback = f"Overall score: {avg_score:.1f}%. See detailed feedback for each question."
        
        # Commit changes
        db.commit()
        
        return submission, student_answers 