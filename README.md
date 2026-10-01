# MORPHE — AI-Powered Universal Research Document Intelligence & Publishing Platform

MORPHE is a production-quality web platform designed to transform raw academic and research documents into structured, validated, analyzed, and publisher-ready artifacts.

## Core Core Lifecycle

**Understand → Structure → Validate → Transform → Publish**

## Key Features

- **Document Ingestion**: Supports `.pdf`, `.docx`, `.txt`, `.md`, and `.tex` parsing with SHA-256 checksum verification.
- **Canonical Document Model (CDM)**: Unified structured semantic JSON representation with full versioning (Version 1, Version 2, etc.) and commit history.
- **NLP Analysis**: Automated extraction of keywords, named entities (methodologies, algorithms, institutions), research terminology, and citation syntax patterns.
- **Domain Intelligence**: Automated classification of research domain (Computer Science, Medicine, Physics, Business, Engineering), subdomain, research type (Experimental, Survey, Case Study, Theoretical), and IMRaD section structure analysis.
- **Validation Engine**: Comprehensive checks for structural completeness, missing metadata, empty sections, and publisher compliance profiles (IEEE, ACM, Elsevier, Springer, Nature).
- **CDM Live Editor**: Structured editing for title, abstract, authors, keywords, sections, and references with instant version commits.
- **AI Research Assistant**: Provider-independent abstraction supporting Google Gemini API with intelligent heuristic offline fallback. Actions include section explanation, academic writing enhancement, abstract generation, and section structuring.
- **Multi-Format Exporters**: Generates publisher-formatted PDF (ReportLab), DOCX (python-docx), LaTeX (.tex), and HTML5 documents.
- **Real Analytics & Dashboard**: Platform statistics calculated directly from database records.

---

## Quick Start Guide

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Run test suite:
```bash
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/test_backend.py
```

Run backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Run with Docker Compose

```bash
docker compose up --build
```

---

## Repository Structure

```text
MORPHE/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API endpoints (Auth, Projects, Docs, CDM, NLP, AI, Validation, Exporters, Analytics)
│   │   ├── core/            # Config, Security, Database engine, Storage manager
│   │   ├── models/          # SQLAlchemy 2.0 ORM models
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   └── modules/         # Ingestion, CDM, NLP, Analysis, Validation, Knowledge, AI, Generation
│   ├── tests/               # Pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages (Dashboard, Projects, Workspace, Knowledge Base, Exports, Analytics)
│   │   ├── components/      # Sidebar, Header, QueryProvider
│   │   ├── context/         # AuthContext
│   │   └── lib/             # Axios API client
│   ├── package.json
│   └── Dockerfile
├── docs/                    # Architecture, API, Development & Database documentation
├── docker-compose.yml
└── .env.example
```
