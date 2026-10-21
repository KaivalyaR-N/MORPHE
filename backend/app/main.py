from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.api.v1.router import api_v1_router
from app.models.models import *  # Ensure all ORM models are registered
from app.modules.knowledge.knowledge_service import KnowledgeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Auto-seed default academic publishers, citation styles & demo user
    async with AsyncSessionLocal() as session:
        await KnowledgeService.seed_knowledge_base(session)

        # Seed default researcher account if not exists
        from app.core.security import get_password_hash
        user_res = await session.execute(select(User).where(User.email == "researcher@morphe.org"))
        if not user_res.scalar_one_or_none():
            demo_user = User(
                email="researcher@morphe.org",
                hashed_password=get_password_hash("Password123!"),
                full_name="Dr. MORPHE Lead Researcher",
                role="RESEARCHER",
                is_active=True
            )
            session.add(demo_user)
            await session.commit()

    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            },
            "detail": exc.detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg_parts = []
    for err in errors:
        loc = ".".join(str(l) for l in err.get("loc", []) if l != "body")
        msg_parts.append(f"{loc}: {err.get('msg', 'Invalid field')}" if loc else err.get("msg", "Invalid field"))
    clean_msg = "; ".join(msg_parts) if msg_parts else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": clean_msg,
                "details": errors
            },
            "detail": clean_msg
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc)
            }
        }
    )


app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }
