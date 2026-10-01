# MORPHE Development & Setup Guide

## Prerequisites

- Python 3.11+
- Node.js v18+ and npm
- Docker & Docker Compose (Optional for containerized run)

## Local Development Setup

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Run tests:
```bash
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/test_backend.py
```

Run FastAPI backend dev server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:3000`.

### 3. Running with Docker Compose

To start all services (PostgreSQL, Redis, FastAPI Backend, Next.js Frontend) in containers:

```bash
docker compose up --build
```
