# MORPHE System Architecture

MORPHE is an **AI-Powered Universal Research Document Intelligence & Publishing Platform**.

## Core Paradigm

MORPHE treats the **Canonical Document Model (CDM)** as the single source of truth:

```text
Original Document (PDF / DOCX / TXT / MD / TEX)
        ↓
   Document Parser
        ↓
Canonical Document Model (CDM Versioning Engine)
        ↓
┌─────────────────┼─────────────────┐
↓                 ↓                 ↓
NLP Analysis   Domain & IMRaD   Validation Engine
                  Classifiers      (Publisher Rules)
        ↓                 ↓                 ↓
        └─────────────────┼─────────────────┘
                          ↓
                   AI Assistant
                          ↓
                 Transformation Engine
                          ↓
        Exporter Abstraction (Pdf, Docx, Latex, Html)
                          ↓
               Publisher-Ready Artifact
```

## Modular Micro-Architecture

### 1. Ingestion Subsystem (`backend/app/modules/ingestion`)
- **PyMuPDF (`fitz`)**: Fast PDF text, section, and metadata extraction.
- **python-docx**: DOCX structured paragraph and title extraction.
- **Regex & Semantic Parsers**: Markdown & LaTeX syntax extractors.
- Calculates SHA-256 checksums to verify document integrity.

### 2. Canonical Document Model (CDM) Engine (`backend/app/modules/cdm`)
- Maintains structured JSON data for Title, Abstract, Authors, Keywords, Sections (hierarchical), Figures, Tables, References, and Citations.
- Every user edit creates a new immutable `DocumentVersion` (Version 1, Version 2, etc.), preserving history.

### 3. NLP & Domain Intelligence (`backend/app/modules/nlp`, `backend/app/modules/analysis`)
- **Keywords & Terminology**: Frequency scoring and research vocabulary identification.
- **Named Entity Recognition**: Categorizes methodologies, algorithms, institutions, and concepts.
- **Domain Classifier**: Classifies papers into Computer Science, Medicine, Physics, Business, Engineering, with confidence scores and evidence trace.
- **IMRaD Structural Analyzer**: Verifies section ordering (Introduction, Methodology, Results, Discussion, Conclusion, References).

### 4. Validation Engine (`backend/app/modules/validation`)
- Checks structural completeness, missing metadata, empty sections, short sections, and citation formats.
- Performs publisher compliance checks against rules for IEEE, ACM, Elsevier, Springer, and Nature.

### 5. AI Assistant Abstraction (`backend/app/modules/ai`)
- Isolated behind `BaseAIProvider` interface.
- Includes `GeminiAIProvider` (via official Google Gemini SDK) and `HeuristicAIProvider` (offline rule engine fallback).

### 6. Multi-Format Exporters (`backend/app/modules/generation`)
- `PdfExporter`: Uses ReportLab to compile clean academic PDFs.
- `DocxExporter`: Uses python-docx to generate Microsoft Word documents.
- `LatexExporter`: Compiles valid `.tex` files with publisher document classes.
- `HtmlExporter`: Generates semantic HTML5 documents styled for web publishing.
