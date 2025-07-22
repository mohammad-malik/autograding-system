# AI-Powered Educational System for Content Generation and Automated Grading

## Overview
This project is a comprehensive AI-powered educational system designed to automate the creation of educational content (slides, quizzes) and the grading of handwritten student responses. By leveraging Large Language Models (LLMs), Optical Character Recognition (OCR), and a modern web interface, the system aims to significantly reduce teacher workload, provide faster feedback to students, and ensure grading consistency at scale.

## Problem Statement
Educators spend excessive time on manual tasks:
- **Content Creation:** 3-8 hours per lecture for slides, notes, and quizzes, with quality and consistency challenges.
- **Grading:** Handwritten quiz grading is slow (2-3 minutes per student), leading to delays and inconsistent feedback.
- **Resource Constraints:** Limited teaching assistants and growing class sizes strain scalability and quality.

## Goals & Objectives
- **Reduce teacher workload by 60-70%** for content creation and grading.
- **Deliver feedback to students within 24 hours.**
- **Maintain or improve educational quality and grading consistency.**
- **Provide actionable analytics for teachers and institutions.**

## Key Features
- **Content Generation:**
  - Upload textbook PDFs, extract and chunk text, generate vector embeddings (OpenAI `text-embedding-3-small`), and store in Pinecone for semantic search.
  - Generate PowerPoint slides and quizzes from textbook content using LLMs (GPT-4o/4.1 or similar).
  - Export generated content as .pptx and .docx files.
- **Quiz Grading:**
  - Upload handwritten quiz photos, preprocess images, and convert handwriting to text using MistralOCR or Google Cloud Vision.
  - LLM-based grading compares OCR'd answers to TA-provided keys, assigns partial credit, and generates detailed feedback.
  - Confidence scoring and human review for unclear cases.
- **Reporting & Analytics:**
  - Individual student reports (scores, feedback, correct answers) and class-wide analytics.
  - Downloadable PDF reports and email notifications.
- **User Interface:**
  - Mobile-responsive web app with dashboards for teachers, TAs, and students.
  - Secure authentication and role-based access control.

## System Architecture
- **Frontend:** React.js SPA for all user roles.
- **Backend:** FastAPI (Python) REST API for business logic, LLM/OCR orchestration, and data management.
- **LLM/OCR Integration:** OpenAI, Anthropic, MistralOCR, Google Cloud Vision.
- **Vector Database:** Pinecone for textbook embeddings and semantic search.
- **Traditional Database:** Supabase + PostgreSQL for user data, quiz metadata, grades, and logs.
- **Cloud Storage:** Supabase Storage (or AWS S3) for PDFs, images, and generated files.
- **Deployment:** AWS (EC2, Lambda), Docker, auto-scaling, and robust backup/recovery.

## Technology Stack
- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, pinecone-client, openai, anthropic, python-pptx, python-docx, PyJWT, pytest
- **Frontend:** React.js, Redux, Axios, Bootstrap CSS
- **Databases:** Pinecone (vector), PostgreSQL (relational), Supabase Storage (files)
- **Cloud:** AWS (EC2, Lambda), Docker

## API Endpoints (Summary)
- `/api/v1/auth/login` — User authentication (JWT)
- `/api/v1/content/upload_textbook` — Upload textbook PDF
- `/api/v1/content/generate_slides` — Generate slides from prompt
- `/api/v1/content/generate_quiz` — Generate quiz from prompt
- `/api/v1/quiz/upload_response` — Upload handwritten quiz image
- `/api/v1/quiz/submit_answer_key` — Submit answer key (TA)
- `/api/v1/quiz/grade_submission/{submission_id}` — Trigger grading
- `/api/v1/reports/student/{student_id}/{quiz_id}` — Get student report
- `/api/v1/reports/class_summary/{quiz_id}` — Get class analytics

## Security & Compliance
- JWT authentication and role-based access
- Data encryption in transit and at rest
- GDPR and UK Data Protection Act compliance
- Prompt injection prevention and audit logs
- Human review for low-confidence OCR and grading

## Success Metrics
- **Content creation time:** 60-70% reduction
- **Quiz grading time:** 80-90% reduction
- **Student feedback:** Within 24 hours
- **Teacher satisfaction:** 90%+
- **AI grading accuracy:** 85%+ correlation with human graders
- **OCR accuracy:** 95%+
- **System uptime:** 99.5%+

## Future Considerations
- LMS integration (Google Classroom, Moodle, etc.)
- Support for video/audio content and interactive materials
- Adaptive learning and personalized recommendations
- Multilingual support
- Advanced analytics and predictive models
- Peer-to-peer learning features

## Getting Started
To run the backend locally:
1. Create a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env` and fill in values.
3. Start the API with `uvicorn app.main:app --reload`.

## License
*To be specified.*
