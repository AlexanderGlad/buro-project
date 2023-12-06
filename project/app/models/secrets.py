import uuid

from sqlmodel import Field, SQLModel


class SecretBase(SQLModel):
    """Базовая модель секретов"""
    secret: str
    secret_phrase: str


class Secret(SecretBase, table=True):
    """Модель секрета для бд"""
    id: int = Field(default=None, nullable=False, primary_key=True)
    secret_key: uuid.UUID = Field(default=None, index=True, nullable=False)


class SecretCreate(SecretBase):
    """Модель секрета при добавлении"""
    pass
