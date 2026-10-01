# MORPHE API Reference (v1)

All endpoints return JSON responses with standard structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

## Endpoints Summary

### Authentication (`/api/v1/auth`)
- `POST /register`: Register user with role (`RESEARCHER`, `REVIEWER`, `EDITOR`, `ADMIN`).
- `POST /login`: JWT authentication returning access and refresh tokens.
- `GET /me`: Return current user profile.

### Projects (`/api/v1/projects`)
- `POST /`: Create project workspace.
- `GET /`: List user projects with document counts.
- `GET /{project_id}`: Get project details.
- `PUT /{project_id}`: Update project title and description.
- `DELETE /{project_id}`: Delete project workspace.

### Documents (`/api/v1/documents`)
- `POST /upload`: Upload PDF, DOCX, TXT, MD, TEX file (starts ingestion, creates CDM v1, runs NLP & validation).
- `GET /project/{project_id}`: List all documents in a project workspace.
- `GET /{document_id}`: Get document metadata.
- `DELETE /{document_id}`: Delete document.

### Canonical Document Model (`/api/v1/cdm`)
- `GET /{document_id}`: Get latest (or versioned) CDM document structure.
- `GET /{document_id}/versions`: Get commit history of all versions.
- `POST /{document_id}/update`: Save CDM edits, creating a new version & re-running analysis.

### Analysis & Intelligence (`/api/v1/analysis`)
- `GET /{document_id}`: Get NLP keywords, named entities, terminology, domain classification, and confidence evidence.

### Validation Engine (`/api/v1/validation`)
- `GET /{document_id}`: Run validation and compliance checks against target publisher (`IEEE`, `ACM`, `ELSEVIER`, `SPRINGER`, `NATURE`).

### Knowledge Base (`/api/v1/knowledge`)
- `GET /publishers`: List publisher profiles & journal guidelines.
- `GET /citation-styles`: List supported citation style rules.

### AI Assistant (`/api/v1/ai`)
- `POST /assistant/{document_id}`: Execute academic AI actions (`explain`, `summarize`, `improve_wording`, `suggest_structure`, `generate_abstract`).

### Generation & Exports (`/api/v1/generation`, `/api/v1/exports`)
- `POST /generation/generate/{document_id}`: Export CDM to PDF, DOCX, LaTeX, or HTML.
- `GET /exports`: List export history.
- `GET /exports/{export_id}/download`: Download generated artifact file.

### Analytics (`/api/v1/analytics`)
- `GET /analytics`: System statistics, file type breakdown, and domain metrics.
