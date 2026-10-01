from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# Standard API Response wrapper
class APIResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


# User & Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "RESEARCHER"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = 0


# Document Schemas
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    original_filename: str
    file_type: str
    sha256_hash: str
    status: str
    created_at: datetime
    updated_at: datetime
    latest_version_number: Optional[int] = 1


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    commit_message: Optional[str]
    created_at: datetime
    cdm_data: Dict[str, Any]


# Canonical Document Model (CDM) Schemas
class CDMAuthor(BaseModel):
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None


class CDMMetadata(BaseModel):
    title: str = ""
    abstract: str = ""
    keywords: List[str] = Field(default_factory=list)
    authors: List[CDMAuthor] = Field(default_factory=list)


class CDMSection(BaseModel):
    id: str
    title: str
    level: int = 1
    content: str = ""
    order: int = 1
    subsections: List["CDMSection"] = Field(default_factory=list)


class CDMFigure(BaseModel):
    id: str
    caption: str
    label: Optional[str] = None
    asset_id: Optional[str] = None


class CDMTable(BaseModel):
    id: str
    caption: str
    label: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)


class CDMReference(BaseModel):
    id: str
    key: str
    text: str
    authors: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    year: Optional[str] = None
    venue: Optional[str] = None
    doi: Optional[str] = None


class CDMCitation(BaseModel):
    id: str
    target_ref_id: str
    location_section_id: str
    raw_text: str


class CDMDocument(BaseModel):
    metadata: CDMMetadata = Field(default_factory=CDMMetadata)
    sections: List[CDMSection] = Field(default_factory=list)
    figures: List[CDMFigure] = Field(default_factory=list)
    tables: List[CDMTable] = Field(default_factory=list)
    references: List[CDMReference] = Field(default_factory=list)
    citations: List[CDMCitation] = Field(default_factory=list)
    appendices: List[CDMSection] = Field(default_factory=list)


# NLP Analysis Schema
class NLPAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_version_id: str
    keywords: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    terminology: List[Dict[str, Any]]
    citation_patterns: Dict[str, Any]
    summary: Optional[str]
    created_at: datetime


# Domain Analysis Schema
class DomainAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_version_id: str
    primary_domain: str
    subdomain: str
    research_type: str
    publication_type: str
    citation_style: str
    confidence: float
    evidence: List[Dict[str, Any]]
    created_at: datetime


# Validation Engine Schema
class ValidationIssue(BaseModel):
    severity: str  # error | warning | info
    category: str  # structure | metadata | citation | content | publisher
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_version_id: str
    structural_issues: List[ValidationIssue]
    metadata_issues: List[ValidationIssue]
    citation_issues: List[ValidationIssue]
    content_issues: List[ValidationIssue]
    publisher_compliance: Dict[str, Any]
    overall_score: float
    created_at: datetime


# Knowledge Base Schemas
class JournalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    publisher_id: str
    name: str
    code: str
    citation_style: str
    required_sections: List[str]
    max_words: Optional[int]
    abstract_max_words: Optional[int]


class PublisherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: Optional[str]
    journals: List[JournalResponse] = Field(default_factory=list)


class CitationStyleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: Optional[str]
    formatting_rules: Dict[str, Any]


# Exporter Schemas
class GenerateExportRequest(BaseModel):
    format: str  # PDF, DOCX, LATEX, HTML
    publisher_code: Optional[str] = "IEEE"


class ExportArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    document_version_id: str
    format: str
    publisher_code: Optional[str]
    file_path: str
    file_size: int
    status: str
    created_at: datetime


# AI Assistant Schemas
class AIAssistantRequest(BaseModel):
    action: str  # explain, summarize, improve_wording, suggest_structure, missing_info, suggest_keywords, explain_validation, suggest_citations, generate_abstract
    prompt: Optional[str] = None
    selected_text: Optional[str] = None
    section_id: Optional[str] = None
    publisher_code: Optional[str] = None


class AIAssistantResponse(BaseModel):
    action: str
    result: str
    suggestions: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    evidence: List[str] = Field(default_factory=list)
