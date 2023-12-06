import base64
import uuid
from typing import Dict, Hashable, Union

from app.errors.api_errors import APIException
from app.models.secrets import Secret, SecretCreate
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(plain_data: str, hashed_data: Hashable) -> bool:
    """Верификация хеша секретной фразы"""
    return pwd_context.verify(plain_data, hashed_data)


def get_hash(hashed_data: str) -> Hashable:
    """Получение хеша секретной фразы"""
    return pwd_context.hash(hashed_data)


def b64_encode(value: str) -> str:
    """Base64 кодирование"""
    encoded_value = base64.b64encode(value.encode()).decode()
    return encoded_value


def b64_decode(value: str) -> str:
    """Base64 декодирование"""
    decoded_value = base64.b64decode(value).decode()
    return decoded_value


def verify_secret(secret: Secret, secret_phrase: str) -> Union[Secret, bool]:
    """Верификация секрета по фразе"""
    if not secret:
        return False
    if not verify_hash(secret_phrase, secret.secret_phrase):
        return False
    return secret


class SecretsRepo:
    """Класс для сервиса секретов"""

    def __init__(self, session: AsyncSession):
        self.db = session

    async def add(self, secret: Secret) -> None:
        """Добавление секрета в бд"""
        self.db.add(secret)
        await self.db.commit()
        await self.db.refresh(secret)

    async def get_by_uuid(self, secret_key: str) -> Union[Secret, None]:
        """Получение секрета из бд"""
        result = await self.db.execute(
            select(Secret).where(Secret.secret_key == secret_key)
        )
        secret = result.scalars().one_or_none()
        return secret

    async def delete(self, secret: Secret) -> None:
        """Удаление секрета из бд"""
        await self.db.delete(secret)
        await self.db.commit()

    async def generate_secret(self, secret_data: SecretCreate) -> Dict[str, uuid.UUID]:
        """Генерация и добавление секрета"""
        secret_b64 = b64_encode(secret_data.secret)
        secret_phrase_hash = get_hash(secret_data.secret_phrase)
        secret_uuid_key = uuid.uuid4()
        secret = Secret(
            secret=secret_b64,
            secret_phrase=secret_phrase_hash,
            secret_key=secret_uuid_key,
        )
        await self.add(secret)

        return {"secret_key": secret_uuid_key}

    async def get_secret(
        self, secret_key: uuid.UUID, secret_phrase: str
    ) -> Dict[str, str]:
        """Получение секрета и удаление из бд"""
        secret = await self.get_by_uuid(secret_key)
        if not secret:
            raise APIException(
                http_code=404,
                error=f"Секрет {secret_key} не найден",
            )
        valid_secret = verify_secret(secret, secret_phrase)

        if not valid_secret:
            raise APIException(
                http_code=400,
                error="Секретная фраза неверна",
            )

        secret_value = b64_decode(secret.secret)
        await self.delete(secret)
        return {"secret": secret_value}
