from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.models.models import Document, DocumentVersion, ValidationResult, Project, User
from app.schemas.schemas import APIResponse, ValidationResultResponse
from app.modules.validation.validation_service import ValidationService
from app.api.deps import get_current_user

router = APIRouter(prefix="/validation", tags=["Validation"])


@router.get("/{document_id}", response_model=APIResponse)
async def get_document_validation(
    document_id: str,
    publisher_code: Optional[str] = Query("IEEE"),
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

    # Re-evaluate validation against specified publisher if publisher_code passed
    val_dict = ValidationService.validate_document(doc_version.cdm_data, target_publisher_code=publisher_code)

    return APIResponse(
        success=True,
        data={
            "document_id": document_id,
            "version_number": doc_version.version_number,
            "target_publisher": publisher_code,
            "validation": val_dict
        }
    )
