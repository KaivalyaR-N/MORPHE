from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.core.database import get_db
from app.models.models import Project, Document, User
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, APIResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=APIResponse)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    resp = ProjectResponse.model_validate(project)
    return APIResponse(success=True, data=resp.model_dump())


@router.get("", response_model=APIResponse)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    project_list = []
    for p in projects:
        # Count documents
        doc_count_res = await db.execute(
            select(func.count(Document.id)).where(Document.project_id == p.id)
        )
        doc_count = doc_count_res.scalar() or 0

        p_dict = ProjectResponse.model_validate(p).model_dump()
        p_dict["document_count"] = doc_count
        project_list.append(p_dict)

    return APIResponse(success=True, data=project_list)


@router.get("/{project_id}", response_model=APIResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    doc_count_res = await db.execute(
        select(func.count(Document.id)).where(Document.project_id == project.id)
    )
    doc_count = doc_count_res.scalar() or 0

    p_dict = ProjectResponse.model_validate(project).model_dump()
    p_dict["document_count"] = doc_count
    return APIResponse(success=True, data=p_dict)


@router.put("/{project_id}", response_model=APIResponse)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description

    await db.commit()
    await db.refresh(project)

    resp = ProjectResponse.model_validate(project)
    return APIResponse(success=True, data=resp.model_dump())


@router.delete("/{project_id}", response_model=APIResponse)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    await db.delete(project)
    await db.commit()
    return APIResponse(success=True, data={"message": "Project deleted successfully."})
