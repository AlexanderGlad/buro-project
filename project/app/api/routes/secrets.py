import uuid

from app.db.db import get_session
from app.models.secrets import SecretCreate
from app.repositories.secrets import SecretsRepo
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/secrets/{secret_key}",
    name="api-secrets:get-secret",
    description="""
## Получение секрета
""",
)
@limiter.limit("600/minute")
async def get_secret(
    request: Request,
    secret_key: uuid.UUID,
    secret_phrase: str,
    session: AsyncSession = Depends(get_session),
):
    """GET /secrets/{secret_key}"""
    secrets_repo = SecretsRepo(session)
    return await secrets_repo.get_secret(secret_key, secret_phrase)


@router.post(
    "/generate",
    name="api-secrets:add-secret",
    description="""
## Добавление секрета
""",
)
@limiter.limit("600/minute")
async def add_secret(
    request: Request,
    secret_data: SecretCreate,
    session: AsyncSession = Depends(get_session)
):
    """POST /generate"""
    secrets_repo = SecretsRepo(session)
    return await secrets_repo.generate_secret(secret_data)
