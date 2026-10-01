# MORPHE Database Schema & Entity Relationships

The platform uses SQLAlchemy 2.0 ORM with asynchronous support for SQLite (development) and PostgreSQL (production).

## Primary Entities

- `User`: Accounts, hashed passwords (bcrypt), roles (`ADMIN`, `RESEARCHER`, `REVIEWER`, `EDITOR`, `GUEST`).
- `Project`: Workspaces owning document collections.
- `Document`: Research document record tracking file type, original filename, SHA-256 hash, and processing status (`UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`).
- `DocumentVersion`: Stores version number (1, 2, 3...) and full Canonical Document Model (`cdm_data` JSON) with commit messages.
- `FileAsset`: Original file reference on storage.
- `NLPAnalysis`: Discovered keywords, named entities, terminology, citation patterns, and summaries tied to a document version.
- `DomainAnalysis`: Primary domain, subdomain, research type, publication type, citation style, confidence score, and evidence list.
- `ValidationResult`: Structural issues, metadata issues, citation issues, content issues, publisher compliance scores, and overall score.
- `Publisher` & `Journal`: Knowledge base entities defining journal constraints, required sections, max words, and citation rules.
- `CitationStyle`: Rules for IEEE, APA, ACM, Chicago, etc.
- `ExportArtifact`: Generated PDF, DOCX, LaTeX, or HTML files with file size, status, and target publisher code.
- `AIConversation`: History of AI assistant interactions per document.
