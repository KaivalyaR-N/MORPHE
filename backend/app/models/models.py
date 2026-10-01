import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Float, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.security import UserRole
import enum


class ProcessingStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.RESEARCHER.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    export_artifacts = relationship("ExportArtifact", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=ProcessingStatus.UPLOADED.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    file_assets = relationship("FileAsset", back_populates="document", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cdm_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    commit_message: Mapped[str] = mapped_column(String(255), nullable=True, default="Initial Ingestion")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="versions")
    nlp_analysis = relationship("NLPAnalysis", back_populates="version", uselist=False, cascade="all, delete-orphan")
    domain_analysis = relationship("DomainAnalysis", back_populates="version", uselist=False, cascade="all, delete-orphan")
    validation_result = relationship("ValidationResult", back_populates="version", uselist=False, cascade="all, delete-orphan")
    export_artifacts = relationship("ExportArtifact", back_populates="version", cascade="all, delete-orphan")


class FileAsset(Base):
    __tablename__ = "file_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="file_assets")


class NLPAnalysis(Base):
    __tablename__ = "nlp_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, unique=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    entities: Mapped[list] = mapped_column(JSON, default=list)
    terminology: Mapped[list] = mapped_column(JSON, default=list)
    citation_patterns: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    version = relationship("DocumentVersion", back_populates="nlp_analysis")


class DomainAnalysis(Base):
    __tablename__ = "domain_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, unique=True)
    primary_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(100), nullable=False)
    research_type: Mapped[str] = mapped_column(String(100), nullable=False)
    publication_type: Mapped[str] = mapped_column(String(100), nullable=False)
    citation_style: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    version = relationship("DocumentVersion", back_populates="domain_analysis")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, unique=True)
    structural_issues: Mapped[list] = mapped_column(JSON, default=list)
    metadata_issues: Mapped[list] = mapped_column(JSON, default=list)
    citation_issues: Mapped[list] = mapped_column(JSON, default=list)
    content_issues: Mapped[list] = mapped_column(JSON, default=list)
    publisher_compliance: Mapped[dict] = mapped_column(JSON, default=dict)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    version = relationship("DocumentVersion", back_populates="validation_result")


class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    journals = relationship("Journal", back_populates="publisher", cascade="all, delete-orphan")


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    publisher_id: Mapped[str] = mapped_column(String(36), ForeignKey("publishers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    citation_style: Mapped[str] = mapped_column(String(50), nullable=False)
    required_sections: Mapped[list] = mapped_column(JSON, default=list)
    max_words: Mapped[int] = mapped_column(Integer, nullable=True)
    abstract_max_words: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    publisher = relationship("Publisher", back_populates="journals")


class CitationStyle(Base):
    __tablename__ = "citation_styles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    formatting_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ExportArtifact(Base):
    __tablename__ = "export_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)  # PDF, DOCX, LATEX, HTML
    publisher_code: Mapped[str] = mapped_column(String(50), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="export_artifacts")
    version = relationship("DocumentVersion", back_populates="export_artifacts")


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    messages: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="ai_conversations")
