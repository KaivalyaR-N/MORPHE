from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.models import Document, DocumentVersion, Project, User
from app.schemas.schemas import APIResponse, AIAssistantRequest, AIAssistantResponse
from app.modules.ai.ai_service import AIService
from app.api.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/assistant/{document_id}", response_model=APIResponse)
async def run_ai_assistant(
    document_id: str,
    request: AIAssistantRequest,
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
        select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc())
    )
    latest_version = v_res.scalars().first()
    if not latest_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No CDM version found.")

    res_dict = await AIService.run_assistant(
        action=request.action,
        prompt=request.prompt,
        selected_text=request.selected_text,
        cdm_data=latest_version.cdm_data,
        publisher_code=request.publisher_code
    )

    resp = AIAssistantResponse.model_validate(res_dict)
    return APIResponse(success=True, data=resp.model_dump())
