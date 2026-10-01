from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from collections import Counter
from app.core.database import get_db
from app.models.models import Document, DomainAnalysis, ExportArtifact, ValidationResult, Project, User
from app.schemas.schemas import APIResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=APIResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Total Projects
    p_res = await db.execute(select(func.count(Project.id)).where(Project.owner_id == current_user.id))
    total_projects = p_res.scalar() or 0

    # Total Documents
    d_res = await db.execute(
        select(Document).join(Project).where(Project.owner_id == current_user.id)
    )
    docs = d_res.scalars().all()
    total_documents = len(docs)

    # File type breakdown
    file_types = Counter([d.file_type.lower() for d in docs])

    # Domain Analysis breakdown
    dom_res = await db.execute(
        select(DomainAnalysis).join(Document, DomainAnalysis.document_version_id == Document.id, isouter=True)
    )
    domain_records = dom_res.scalars().all()

    domains_detected = Counter([d.primary_domain for d in domain_records if d.primary_domain])
    research_types = Counter([d.research_type for d in domain_records if d.research_type])
    citation_styles = Counter([d.citation_style for d in domain_records if d.citation_style])

    # Validation scores
    val_res = await db.execute(select(ValidationResult.overall_score))
    scores = val_res.scalars().all()
    avg_score = round(sum(scores) / len(scores), 1) if scores else 90.0

    # Total Exports
    e_res = await db.execute(
        select(ExportArtifact).join(Project).where(Project.owner_id == current_user.id)
    )
    exports = e_res.scalars().all()
    total_exports = len(exports)
    publisher_usage = Counter([e.publisher_code for e in exports if e.publisher_code])

    return APIResponse(
        success=True,
        data={
            "total_projects": total_projects,
            "total_documents": total_documents,
            "total_exports": total_exports,
            "average_validation_score": avg_score,
            "file_types": [{"name": k.upper(), "count": v} for k, v in file_types.items()],
            "domains_detected": [{"name": k, "count": v} for k, v in domains_detected.items()],
            "research_types": [{"name": k, "count": v} for k, v in research_types.items()],
            "citation_styles": [{"name": k, "count": v} for k, v in citation_styles.items()],
            "publisher_usage": [{"name": k, "count": v} for k, v in publisher_usage.items()]
        }
    )
