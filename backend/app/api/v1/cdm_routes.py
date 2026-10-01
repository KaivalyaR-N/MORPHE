from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, Optional
from app.core.database import get_db
from app.models.models import (
    Document, DocumentVersion, Project, User,
    NLPAnalysis, DomainAnalysis, ValidationResult
)
from app.schemas.schemas import APIResponse, DocumentVersionResponse
from app.modules.nlp.nlp_service import NLPService
from app.modules.analysis.domain_service import DomainIntelligenceService
from app.modules.validation.validation_service import ValidationService
from app.api.deps import get_current_user

router = APIRouter(prefix="/cdm", tags=["CDM"])


@router.get("/{document_id}", response_model=APIResponse)
async def get_latest_cdm(
    document_id: str,
    version: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if version:
        v_res = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version
            )
        )
        doc_version = v_res.scalar_one_or_none()
    else:
        v_res = await db.execute(
            select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc())
        )
        doc_version = v_res.scalars().first()

    if not doc_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CDM version not found.")

    resp = DocumentVersionResponse.model_validate(doc_version)
    return APIResponse(success=True, data=resp.model_dump())


@router.get("/{document_id}/versions", response_model=APIResponse)
async def get_document_versions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    if not doc_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    v_res = await db.execute(
        select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc())
    )
    versions = v_res.scalars().all()

    ver_list = []
    for v in versions:
        ver_list.append({
            "id": v.id,
            "version_number": v.version_number,
            "commit_message": v.commit_message,
            "created_at": v.created_at
        })

    return APIResponse(success=True, data=ver_list)


@router.post("/{document_id}/update", response_model=APIResponse)
async def update_cdm(
    document_id: str,
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    cdm_data = payload.get("cdm_data")
    commit_message = payload.get("commit_message", "Updated document via CDM Editor")

    if not cdm_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing cdm_data payload.")

    # Update document title if metadata title updated
    new_title = cdm_data.get("metadata", {}).get("title")
    if new_title:
        document.title = new_title

    # Determine next version number
    v_res = await db.execute(
        select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == document_id)
    )
    curr_max = v_res.scalar() or 0
    new_version_num = curr_max + 1

    new_version = DocumentVersion(
        document_id=document_id,
        version_number=new_version_num,
        cdm_data=cdm_data,
        commit_message=commit_message
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)

    # Re-run NLP, Domain Intelligence, and Validation for the new version
    nlp_dict = NLPService.analyze_cdm(cdm_data)
    nlp_record = NLPAnalysis(
        document_version_id=new_version.id,
        keywords=nlp_dict.get("keywords", []),
        entities=nlp_dict.get("entities", []),
        terminology=nlp_dict.get("terminology", []),
        citation_patterns=nlp_dict.get("citation_patterns", {}),
        summary=nlp_dict.get("summary")
    )
    db.add(nlp_record)

    domain_dict = DomainIntelligenceService.analyze_domain_and_structure(cdm_data)
    d_info = domain_dict["domain_analysis"]
    domain_record = DomainAnalysis(
        document_version_id=new_version.id,
        primary_domain=d_info["primary_domain"],
        subdomain=d_info["subdomain"],
        research_type=d_info["research_type"],
        publication_type=d_info["publication_type"],
        citation_style=d_info["citation_style"],
        confidence=d_info["confidence"],
        evidence=d_info["evidence"]
    )
    db.add(domain_record)

    val_dict = ValidationService.validate_document(cdm_data, target_publisher_code="IEEE")
    val_record = ValidationResult(
        document_version_id=new_version.id,
        structural_issues=val_dict["structural_issues"],
        metadata_issues=val_dict["metadata_issues"],
        citation_issues=val_dict["citation_issues"],
        content_issues=val_dict["content_issues"],
        publisher_compliance=val_dict["publisher_compliance"],
        overall_score=val_dict["overall_score"]
    )
    db.add(val_record)

    await db.commit()

    resp = DocumentVersionResponse.model_validate(new_version)
    return APIResponse(success=True, data=resp.model_dump())
