from fastapi import APIRouter
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.project_routes import router as project_router
from app.api.v1.document_routes import router as document_router
from app.api.v1.cdm_routes import router as cdm_router
from app.api.v1.analysis_routes import router as analysis_router
from app.api.v1.validation_routes import router as validation_router
from app.api.v1.knowledge_routes import router as knowledge_router
from app.api.v1.ai_routes import router as ai_router
from app.api.v1.generation_routes import router as generation_router
from app.api.v1.export_routes import router as export_router
from app.api.v1.analytics_routes import router as analytics_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(project_router)
api_v1_router.include_router(document_router)
api_v1_router.include_router(cdm_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(validation_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(generation_router)
api_v1_router.include_router(export_router)
api_v1_router.include_router(analytics_router)
