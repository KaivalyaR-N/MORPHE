from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.storage import storage_service
from app.models.models import Document, DocumentVersion, ExportArtifact, Project, User
from app.schemas.schemas import APIResponse, GenerateExportRequest, ExportArtifactResponse
from app.modules.generation.exporters import ExporterFactory
from app.api.deps import get_current_user

router = APIRouter(prefix="/generation", tags=["Document Generation"])


@router.post("/generate/{document_id}", response_model=APIResponse)
async def generate_document_export(
    document_id: str,
    req: GenerateExportRequest,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No CDM version found for document.")

    publisher_code = req.publisher_code or "IEEE"
    exporter = ExporterFactory.get_exporter(req.format)

    try:
        file_bytes, ext, mime_type = exporter.export(latest_version.cdm_data, publisher_code=publisher_code)
        file_path, file_size = storage_service.save_export_artifact(
            file_bytes, file_extension=ext, prefix=f"{req.format.lower()}_{publisher_code.lower()}"
        )

        artifact = ExportArtifact(
            project_id=document.project_id,
            document_version_id=latest_version.id,
            format=req.format.upper(),
            publisher_code=publisher_code,
            file_path=file_path,
            file_size=file_size,
            status="COMPLETED"
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)

        resp = ExportArtifactResponse.model_validate(artifact)
        return APIResponse(success=True, data=resp.model_dump())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export generation failed: {str(e)}"
        )
