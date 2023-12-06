from app.api.routes.secrets import router as secrets
from fastapi import APIRouter

router = APIRouter()


router.include_router(secrets, prefix="", tags=["api-secrets"])
