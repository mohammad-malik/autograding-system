import json
from typing import Dict, List, Optional, Tuple, Any

from ..models import TaskStatus
from ..models.supabase_client import table, get_by_id, insert, update_by_id
from ..services import LLMClient


class GradingSystem:
    """Grading system for quiz submissions."""

    @staticmethod
    async def grade_submission(
        submission_id: str,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Grade quiz submission."""
        # Get submission
        submission = get_by_id("submissions", submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")
        
        # Check if OCR was successful
        if submission["status"] != TaskStatus.COMPLETED:
            update_by_id("submissions", submission_id, {"status": TaskStatus.FAILED})
            return submission, []
        
        # Get quiz questions
        questions = (
            table("quiz_questions")
            .select("*")
            .eq("quiz_id", submission["quiz_id"])
            .execute()
            .data
        )
        if not questions:
            update_by_id(
                "submissions",
                submission_id,
                {
                    "status": TaskStatus.FAILED,
                    "llm_feedback": "No questions found for this quiz",
                },
            )
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
            answer_key_row = (
                table("answer_key_details")
                .select("*")
                .eq("question_id", question["id"])
                .single()
                .execute()
                .data
            )
            if not answer_key_row:
                continue
            
            # Get student answer
            student_answer_text = answers.get(i + 1, "")
            
            # Grade answer
            keywords = answer_key_row.get("keywords")
            grade_result = await LLMClient.grade_submission(
                student_answer_text,
                question["question_text"],
                answer_key_row["correct_text_or_choice"],
                keywords,
            )
            
            # Create student answer record
            answer_record = insert(
                "grades",
                {
                    "submission_id": submission_id,
                    "question_id": question["id"],
                    "assigned_score": grade_result["score"],
                    "llm_feedback": grade_result["feedback"],
                },
            )
            student_answers.append(answer_record)
            
            # Add to total score
            total_score += grade_result["score"]
        
        # Calculate average score
        avg_score = total_score / total_questions if total_questions > 0 else 0
        
        # Update submission
        update_by_id(
            "submissions",
            submission_id,
            {
                "score": avg_score,
                "status": TaskStatus.COMPLETED,
                "llm_feedback": f"Overall score: {avg_score:.1f}%.",
            },
        )
        
        submission["score"] = avg_score
        submission["status"] = TaskStatus.COMPLETED
        return submission, student_answers 