import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.models import ExportArtifact, Project, User
from app.schemas.schemas import APIResponse, ExportArtifactResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/exports", tags=["Exports Management"])


@router.get("", response_model=APIResponse)
async def list_exports(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(ExportArtifact).join(Project).where(Project.owner_id == current_user.id)
    if project_id:
        query = query.where(ExportArtifact.project_id == project_id)

    query = query.order_by(ExportArtifact.created_at.desc())
    result = await db.execute(query)
    artifacts = result.scalars().all()

    art_list = [ExportArtifactResponse.model_validate(a).model_dump() for a in artifacts]
    return APIResponse(success=True, data=art_list)


@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(ExportArtifact).join(Project).where(ExportArtifact.id == export_id, Project.owner_id == current_user.id)
    result = await db.execute(query)
    artifact = result.scalar_one_or_none()

    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export artifact not found.")

    if not os.path.exists(artifact.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact file does not exist on disk.")

    filename = os.path.basename(artifact.file_path)
    return FileResponse(
        path=artifact.file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
