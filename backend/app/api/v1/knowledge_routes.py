from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import APIResponse
from app.modules.knowledge.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.get("/publishers", response_model=APIResponse)
async def list_publishers(db: AsyncSession = Depends(get_db)):
    publishers = await KnowledgeService.get_publishers_from_db(db)
    return APIResponse(success=True, data=publishers)


@router.get("/publishers/{code}", response_model=APIResponse)
async def get_publisher(code: str):
    pub = KnowledgeService.get_publisher_by_code(code)
    if not pub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found.")
    return APIResponse(success=True, data=pub)


@router.get("/citation-styles", response_model=APIResponse)
@router.get("/styles", response_model=APIResponse)
async def list_citation_styles():
    styles = KnowledgeService.get_citation_styles()
    return APIResponse(success=True, data=styles)
