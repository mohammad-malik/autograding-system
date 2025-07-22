# AI-Powered Educational System

This system automates educational content generation and handwritten quiz grading to reduce teachers' workload and provide faster feedback to students.

## Features

- **Content Generation**
  - PDF textbook processing and vectorization
  - AI-powered slide generation (.pptx)
  - AI-powered quiz generation (.docx)
  
- **Quiz Assessment**
  - Handwritten quiz processing via OCR
  - AI-driven grading with partial credit
  - Detailed student feedback
  
- **Reporting**
  - Individual student reports
  - Class-wide analytics
  - PDF report generation

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic, Pinecone, OpenAI, MistralOCR
- **Frontend**: React, TypeScript, Material-UI
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Authentication**: JWT, Supabase Auth

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- Docker and Docker Compose (optional)

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/autograding-system.git
   cd autograding-system
   ```

2. Create and activate a conda environment:
   ```
   conda create -n autograding python=3.10
   conda activate autograding
   ```

3. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

5. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```

### Running the Application

#### Backend

```
cd backend
uvicorn app.main:app --reload
```

#### Frontend

```
cd frontend
npm start
```

#### Using Docker (optional)

```
docker-compose up
```

## Project Structure

```
autograding-system/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entrypoint
│   │   ├── config.py             # Environment config
│   │   ├── auth/                 # JWT auth, user roles
│   │   ├── content/              # PDF processing, embeddings
│   │   ├── quiz/                 # OCR upload, grading
│   │   ├── reports/              # PDF report generation
│   │   ├── services/             # LLM, OCR, Pinecone clients
│   │   └── models/               # Pydantic schemas
│   └── tests/                    # pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Dashboard pages
│   │   ├── services/             # API client, auth
│   │   ├── App.tsx               # Main React app
│   │   └── index.tsx             # Entrypoint
│   └── public/
├── .env.example                  # Environment template
├── docker-compose.yml            # Docker setup
└── README.md                     # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
