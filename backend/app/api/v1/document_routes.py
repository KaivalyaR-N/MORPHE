from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.core.storage import storage_service
from app.models.models import (
    Document, DocumentVersion, FileAsset, Project, User,
    NLPAnalysis, DomainAnalysis, ValidationResult, ProcessingStatus
)
from app.schemas.schemas import APIResponse, DocumentResponse, DocumentVersionResponse
from app.modules.ingestion.parser import DocumentParser
from app.modules.cdm.cdm_service import CDMService
from app.modules.nlp.nlp_service import NLPService
from app.modules.analysis.domain_service import DomainIntelligenceService
from app.modules.validation.validation_service import ValidationService
from app.api.deps import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=APIResponse)
async def upload_document(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify project ownership
    proj_res = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    # Read and save file content
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    target_path, sha256_hash, file_size, ext = storage_service.save_uploaded_file(
        content, file.filename
    )

    doc_title = file.filename.rsplit(".", 1)[0].replace("_", " ").title()

    document = Document(
        project_id=project_id,
        title=doc_title,
        original_filename=file.filename,
        file_type=ext.lstrip("."),
        sha256_hash=sha256_hash,
        status=ProcessingStatus.PROCESSING.value
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # File asset record
    asset = FileAsset(
        document_id=document.id,
        file_type=ext.lstrip("."),
        file_path=target_path,
        file_size=file_size,
        sha256_hash=sha256_hash
    )
    db.add(asset)

    try:
        # Ingestion pipeline: Parse -> CDM -> NLP -> Domain -> Validation
        parsed_data = DocumentParser.parse_file(target_path, ext)
        if parsed_data.get("title") and parsed_data["title"] != "Untitled Document":
            document.title = parsed_data["title"]

        cdm_data = CDMService.build_initial_cdm(parsed_data)

        # Version 1 creation
        doc_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            cdm_data=cdm_data,
            commit_message="Initial Document Ingestion"
        )
        db.add(doc_version)
        await db.commit()
        await db.refresh(doc_version)

        # NLP Analysis
        nlp_dict = NLPService.analyze_cdm(cdm_data)
        nlp_record = NLPAnalysis(
            document_version_id=doc_version.id,
            keywords=nlp_dict.get("keywords", []),
            entities=nlp_dict.get("entities", []),
            terminology=nlp_dict.get("terminology", []),
            citation_patterns=nlp_dict.get("citation_patterns", {}),
            summary=nlp_dict.get("summary")
        )
        db.add(nlp_record)

        # Domain Intelligence & Structure
        domain_dict = DomainIntelligenceService.analyze_domain_and_structure(cdm_data)
        d_info = domain_dict["domain_analysis"]
        domain_record = DomainAnalysis(
            document_version_id=doc_version.id,
            primary_domain=d_info["primary_domain"],
            subdomain=d_info["subdomain"],
            research_type=d_info["research_type"],
            publication_type=d_info["publication_type"],
            citation_style=d_info["citation_style"],
            confidence=d_info["confidence"],
            evidence=d_info["evidence"]
        )
        db.add(domain_record)

        # Validation Engine
        val_dict = ValidationService.validate_document(cdm_data, target_publisher_code="IEEE")
        val_record = ValidationResult(
            document_version_id=doc_version.id,
            structural_issues=val_dict["structural_issues"],
            metadata_issues=val_dict["metadata_issues"],
            citation_issues=val_dict["citation_issues"],
            content_issues=val_dict["content_issues"],
            publisher_compliance=val_dict["publisher_compliance"],
            overall_score=val_dict["overall_score"]
        )
        db.add(val_record)

        document.status = ProcessingStatus.COMPLETED.value
        await db.commit()
        await db.refresh(document)

        doc_resp = DocumentResponse.model_validate(document).model_dump()
        doc_resp["latest_version_number"] = 1
        return APIResponse(success=True, data=doc_resp)

    except Exception as e:
        document.status = ProcessingStatus.FAILED.value
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=APIResponse)
async def list_project_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify project
    proj_res = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    if not proj_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    result = await db.execute(
        select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    doc_list = []
    for d in docs:
        v_res = await db.execute(
            select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == d.id)
        )
        max_ver = v_res.scalar() or 1

        d_dict = DocumentResponse.model_validate(d).model_dump()
        d_dict["latest_version_number"] = max_ver
        doc_list.append(d_dict)

    return APIResponse(success=True, data=doc_list)


@router.get("/{document_id}", response_model=APIResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    v_res = await db.execute(
        select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == document.id)
    )
    max_ver = v_res.scalar() or 1

    d_dict = DocumentResponse.model_validate(document).model_dump()
    d_dict["latest_version_number"] = max_ver
    return APIResponse(success=True, data=d_dict)


@router.delete("/{document_id}", response_model=APIResponse)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    await db.delete(document)
    await db.commit()
    return APIResponse(success=True, data={"message": "Document deleted successfully."})
