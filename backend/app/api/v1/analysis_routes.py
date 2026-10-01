from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.models.models import Document, DocumentVersion, NLPAnalysis, DomainAnalysis, Project, User
from app.schemas.schemas import APIResponse, NLPAnalysisResponse, DomainAnalysisResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/{document_id}", response_model=APIResponse)
async def get_document_analysis(
    document_id: str,
    version: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(
        select(Document).join(Project).where(Document.id == document_id, Project.owner_id == current_user.id)
    )
    if not doc_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if version:
        v_res = await db.execute(
            select(DocumentVersion).where(DocumentVersion.document_id == document_id, DocumentVersion.version_number == version)
        )
        doc_version = v_res.scalar_one_or_none()
    else:
        v_res = await db.execute(
            select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc())
        )
        doc_version = v_res.scalars().first()

    if not doc_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document version not found.")

    nlp_res = await db.execute(
        select(NLPAnalysis).where(NLPAnalysis.document_version_id == doc_version.id)
    )
    nlp_rec = nlp_res.scalar_one_or_none()

    dom_res = await db.execute(
        select(DomainAnalysis).where(DomainAnalysis.document_version_id == doc_version.id)
    )
    dom_rec = dom_res.scalar_one_or_none()

    nlp_data = NLPAnalysisResponse.model_validate(nlp_rec).model_dump() if nlp_rec else None
    dom_data = DomainAnalysisResponse.model_validate(dom_rec).model_dump() if dom_rec else None

    return APIResponse(
        success=True,
        data={
            "version_number": doc_version.version_number,
            "nlp_analysis": nlp_data,
            "domain_analysis": dom_data
        }
    )
