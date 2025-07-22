# autograding-system Development Agent Guide

This document provides detailed guidance for coding agents to implement the AI-Powered Educational System for Content Generation and Automated Grading. It outlines architecture, directory structure, technology stack, API contracts, modules, dependencies, and best practices.

---

## 1. Project Overview

- Objective: Build a FastAPI backend + React frontend system that automates:
  - Educational content generation (slides, quizzes) from textbook PDFs.
  - Handwritten quiz grading via OCR + LLM-based grading.

- Key Features:
  - PDF upload, text extraction, content chunking, embeddings (Pinecone).
  - GPT-4o/4.1-powered slide & quiz generation (.pptx, .docx).
  - MistralOCR (fallback TrOCR/Google Vision) for handwritten text conversion.
  - LLM-driven grading with partial credit, chain-of-thought, detailed feedback.
  - Reporting: individual PDF reports, class analytics, email notifications.
  - User roles: Teacher, TA, Student. JWT-based auth, Supabase (Postgres + storage).

## 2. Architecture Overview

- Microservices-like monorepo:
  - **Backend (FastAPI)**: `/backend` directory.
  - **Frontend (React)**: `/frontend` directory.
  - **Shared Config & Scripts**: root-level.

- External integrations:
  - Pinecone vector DB for embeddings.
  - OpenAI API (embeddings & completions).
  - MistralOCR (or fallback) for handwritten OCR.
  - Supabase for authentication, Postgres, and file storage.

## 3. Directory Structure

```bash
autograding-system/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entrypoint
│   │   ├── config.py             # Environment config (Pydantic)
│   │   ├── auth/                 # JWT auth, user roles, Supabase client
│   │   ├── content/              # PDF processing, embeddings, slide & quiz generation
│   │   ├── quiz/                 # OCR upload, grading endpoints
│   │   ├── reports/              # PDF report generation, analytics
│   │   ├── services/             # LLM client, OCR client, Pinecone client, storage client
│   │   └── models/               # Pydantic schemas, DB models
│   └── tests/                    # pytest unit & integration tests
└── frontend/
    ├── src/
    │   ├── components/           # Reusable React components
    │   ├── pages/                # Teacher, TA, Student dashboards
    │   ├── services/             # API client (axios), auth
    │   ├── App.tsx               # Main React app
    │   └── index.tsx             # Entrypoint
    ├── public/
 # autograding-system Development Agent Guide

 This document provides detailed guidance for coding agents to implement the AI-Powered Educational System for Content Generation and Automated Grading. It outlines architecture, directory structure, technology stack, API contracts, modules, dependencies, and best practices.

 ---

 ## 1. Project Overview

 - Objective:
   - Educational content generation (slides, quizzes) from textbook PDFs
   - Handwritten quiz grading via OCR + LLM-based grading

 - Key Features:
   - PDF upload, text extraction, content chunking, embeddings (Pinecone)
   - GPT-4o/4.1 slide & quiz generation (.pptx, .docx)
   - MistralOCR (fallback TrOCR/Google Vision) for handwritten text conversion
   - LLM-driven grading with partial credit, chain-of-thought, detailed feedback
   - Reporting: individual PDF reports, class analytics, email notifications
   - Role-based access: Teacher, TA, Student with JWT auth and Supabase storage

 ## 2. Architecture Overview

 - Monorepo structure:
   - Backend: FastAPI service in `/backend`
   - Frontend: React (TypeScript) in `/frontend`
   - Shared configs, Docker files, CI scripts at root

 - External services:
   - Pinecone for embeddings storage
   - OpenAI API for embeddings & text generation
   - MistralOCR (fallback to Google Vision/TrOCR) for handwritten OCR
   - Supabase for Postgres DB, auth, and storage

 ## 3. Directory Structure

 ```bash
 autograding-system/
 ├── backend/
 │   ├── app/
 │   │   ├── main.py            # FastAPI entry
 │   │   ├── config.py          # Pydantic settings
 │   │   ├── auth/              # JWT & Supabase client
 │   │   ├── content/           # PDF processing & embeddings
 │   │   ├── quiz/              # OCR & grading endpoints
 │   │   ├── reports/           # PDF report generation
 │   │   ├── services/          # LLM, OCR, Pinecone, Supabase clients
 │   │   └── models/            # Pydantic & DB schemas
 │   └── tests/                 # pytest suites
 ├── frontend/
 │   ├── src/
 │   │   ├── components/        # Reusable UI components
 │   │   ├── pages/             # Teacher/TA/Student dashboards
 │   │   ├── services/          # API client & auth hooks
 │   │   ├── App.tsx            # React root
 │   │   └── index.tsx          # Webpack entry
 │   └── package.json
 ├── .env.example               # Env vars template
 ├── docker-compose.yml         # Local dev setup
 ├── Dockerfile.backend
 ├── Dockerfile.frontend
 └── README.md                  # Setup & run instructions
 ```

## 4. Technology Stack

 - **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic, Pinecone-client, OpenAI, python-pptx, python-docx, MistralOCR/google-cloud-vision, supabase-py, ReportLab/fpdf2, pytest, httpx
 - **Frontend**: React, TypeScript, React Router, Axios, Context API or Redux, Material-UI or Chakra UI, Jest, React Testing Library

## 5. Configuration

 - Copy `.env.example` to `.env` and set:
   - OPENAI_API_KEY
   - PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX
   - SUPABASE_URL, SUPABASE_KEY
   - MISTRALOCR_API_KEY
   - JWT_SECRET_KEY, JWT_ALGORITHM

## 6. API Endpoints

 | Path                                  | Method | Description                                  | Roles       |
 |---------------------------------------|--------|----------------------------------------------|-------------|
 | /api/v1/auth/register                 | POST   | Create user                                  | Public      |
 | /api/v1/auth/login                    | POST   | Authenticate & return JWT token              | Public      |
 | /api/v1/content/upload_textbook       | POST   | Upload PDF & index embeddings                | Teacher     |
 | /api/v1/content/generate_slides       | POST   | Generate PPTX slides                         | Teacher     |
 | /api/v1/content/generate_quiz         | POST   | Generate DOCX quiz                           | Teacher     |
 | /api/v1/quiz/upload_response          | POST   | OCR handwritten responses                    | Student     |
 | /api/v1/quiz/submit_answer_key        | POST   | Submit correct answers                       | TA          |
 | /api/v1/quiz/grade_submission         | POST   | Trigger AI grading                           | TA/Teacher  |
 | /api/v1/reports/student/{submission}  | GET    | Download student report PDF                  | Student/TA  |
 | /api/v1/reports/class_summary/{quiz}  | GET    | Download class analytics PDF                 | TA/Teacher  |

## 7. Backend Modules

 - **auth**: Supabase client, JWT creation & validation, role-based dependencies
 - **content**: PDF parsing (PyMuPDF/MistralOCR), chunking (LangChain), embeddings (OpenAI), Pinecone upsert, slide & quiz generation (LLM + python-pptx/docx)
 - **quiz**: OCR upload (OpenCV + MistralOCR), store text, answer key management, AI grading (LLM with CoT), partial credit
 - **reports**: PDF generation (ReportLab/fpdf2), analytics (Pandas), storage (Supabase)

## 8. Frontend Structure

 - Global auth context for JWT management
 - Protected routes per user role
 - Components:
   - FileUploader
   - SlideGeneratorForm
   - QuizGeneratorForm
   - OCRUpload
   - GradingReviewTable (TA review)
   - ReportsPage & AnalyticsCharts

 ## 9. Testing & Quality

 - **Backend**: pytest + httpx for endpoints
 - **Frontend**: Jest + React Testing Library for UI
 - **Linting**: flake8/black and ESLint/Prettier

 ## 10. CI/CD

 - GitHub Actions to lint, test, build Docker images, and deploy to AWS (ECS/EKS)
 - `docker-compose.yml` for local integration

 ## 11. Coding Standards

 - Use type hints and Pydantic models
 - Modular code with clear separation of concerns
 - Robust error handling and structured logging
 - Input validation and RBAC on all endpoints
 - Document public interfaces and modules
 - Use conda environment "mistral"

 ---

 *End of agent guide.*
 - Secure all endpoints with RBAC and input validation.
 - Document public functions and modules.

 ---

 *This guide equips coding agents with a roadmap to implement the autograding-system in a systematic, modular, and test-driven manner.*