import json
from typing import Dict, List, Optional, Union, Any

import openai
import anthropic
from openai.types.chat import ChatCompletion
# from dotenv import load_dotenv  # redundant

# load_dotenv()  # redundant

from ..config import get_settings

# Initialize clients
openai.api_key = get_settings().openai_api_key
anthropic_client = anthropic.Anthropic(api_key=get_settings().anthropic_api_key) if get_settings().anthropic_api_key else None


class LLMClient:
    """Client for LLM services."""

    @staticmethod
    async def generate_text(
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> str:
        """Generate text using OpenAI API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response: ChatCompletion = await openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else None,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to Anthropic if available
            if anthropic_client:
                return await LLMClient.generate_text_anthropic(prompt, system_prompt, temperature, max_tokens)
            raise e

    @staticmethod
    async def generate_text_anthropic(
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate text using Anthropic API."""
        if not anthropic_client:
            raise ValueError("Anthropic API key not set")

        system = system_prompt if system_prompt else ""
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content[0].text

    @staticmethod
    async def generate_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        response = await openai.embeddings.create(
            model=model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    @staticmethod
    async def generate_slides(
        prompt: str,
        context: str,
        num_slides: int,
    ) -> Dict[str, Any]:
        """Generate slide content using LLM."""
        system_prompt = """You are an expert educator and content creator. 
        Your task is to create well-structured, informative, and engaging PowerPoint slides based on the provided context.
        The output should be a JSON object with an array of slide objects, each containing:
        - title: The slide title
        - content: Array of bullet points for the slide
        - notes: Speaker notes for the slide
        Make sure the content is accurate, well-organized, and follows a logical flow."""

        prompt_template = f"""
        Create {num_slides} PowerPoint slides based on the following prompt and context:
        
        PROMPT: {prompt}
        
        CONTEXT:
        {context}
        
        Return a JSON object with the following structure:
        {{
            "slides": [
                {{
                    "title": "Slide Title",
                    "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
                    "notes": "Speaker notes for this slide."
                }},
                ...
            ]
        }}
        """

        response = await LLMClient.generate_text(
            prompt=prompt_template,
            system_prompt=system_prompt,
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4000,
            json_mode=True,
        )
        return json.loads(response)

    @staticmethod
    async def generate_quiz(
        prompt: str,
        context: str,
        question_types: List[str],
        difficulty: str,
    ) -> Dict[str, Any]:
        """Generate quiz content using LLM."""
        system_prompt = """You are an expert educator specializing in assessment design.
        Your task is to create high-quality quiz questions based on the provided context.
        The output should be a JSON object with an array of question objects.
        Make sure the questions are accurate, clear, and appropriate for the specified difficulty level."""

        prompt_template = f"""
        Create a quiz based on the following prompt, context, question types, and difficulty:
        
        PROMPT: {prompt}
        
        CONTEXT:
        {context}
        
        QUESTION TYPES: {", ".join(question_types)}
        
        DIFFICULTY: {difficulty}
        
        Return a JSON object with the following structure:
        {{
            "title": "Quiz Title",
            "description": "Brief description of the quiz",
            "questions": [
                {{
                    "id": "q1",
                    "type": "multiple_choice",
                    "text": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Explanation of the correct answer"
                }},
                {{
                    "id": "q2",
                    "type": "short_answer",
                    "text": "Question text",
                    "correct_answer": "Correct answer",
                    "keywords": ["keyword1", "keyword2"],
                    "explanation": "Explanation of the correct answer"
                }},
                ...
            ]
        }}
        """

        response = await LLMClient.generate_text(
            prompt=prompt_template,
            system_prompt=system_prompt,
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4000,
            json_mode=True,
        )

        return json.loads(response)

    @staticmethod
    async def grade_submission(
        student_answer: str,
        question: str,
        correct_answer: str,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Grade student submission using LLM."""
        system_prompt = """You are an expert grader with deep knowledge in education and assessment.
        Your task is to grade a student's answer to a question, comparing it to the correct answer.
        You should provide a score (0-100), feedback, and justification for the score.
        Consider partial credit for partially correct answers.
        Be fair, consistent, and provide constructive feedback."""

        prompt_template = f"""
        Grade the following student answer to a question:
        
        QUESTION: {question}
        
        CORRECT ANSWER: {correct_answer}
        
        STUDENT ANSWER: {student_answer}
        
        {"KEYWORDS: " + ", ".join(keywords) if keywords else ""}
        
        Return a JSON object with the following structure:
        {{
            "score": 85,
            "feedback": "Your answer was mostly correct, but you missed...",
            "justification": "I gave this score because..."
        }}
        
        Use a chain-of-thought approach to explain your reasoning before determining the final score.
        """

        response = await LLMClient.generate_text(
            prompt=prompt_template,
            system_prompt=system_prompt,
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2000,
            json_mode=True,
        )

        return json.loads(response) 