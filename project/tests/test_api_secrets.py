import pytest
from fastapi import FastAPI
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


negative_post_data = [
    ({}, 400, {"error": "Не указан обязательный параметр secret: UNKNOWN"}),
    (
        {"secret": "test"},
        400,
        {"error": "Не указан обязательный параметр secret_phrase: UNKNOWN"},
    ),
]

positiv_post_data = [
    ({"secret": "test", "secret_phrase": "string"}, 200),
]


class TestApiSecrets:
    """api-secrets Test Class"""

    @pytest.mark.parametrize("data, status_code, response_data", negative_post_data)
    async def test_negative_add_secret(
        self,
        app: FastAPI,
        client: AsyncClient,
        data: dict,
        status_code: int,
        response_data: dict,
    ) -> None:
        """Негативные сценарии для проверки обязательных параметров"""
        res = await client.post(app.url_path_for("api-secrets:add-secret"), json=data)
        assert res.status_code == status_code
        assert res.json() == response_data

    @pytest.mark.parametrize("data, status_code", positiv_post_data)
    async def test_positiv_add_secret(
        self, app: FastAPI, client: AsyncClient, data: dict, status_code: int
    ) -> None:
        """Позитивный сценарий добавления, получения и удаления секрета"""
        res_add = await client.post(
            app.url_path_for("api-secrets:add-secret"), json=data
        )
        assert res_add.status_code == status_code

        secret_key = res_add.json()["secret_key"]

        res_get = await client.get(
            app.url_path_for("api-secrets:get-secret", secret_key=secret_key),
            params={"secret_phrase": data["secret_phrase"]},
        )

        assert res_get.status_code == 200
        assert res_get.json() == {"secret": data["secret"]}

        res_get2 = await client.get(
            app.url_path_for("api-secrets:get-secret", secret_key=secret_key),
            params={"secret_phrase": data["secret_phrase"]},
        )

        assert res_get2.status_code == 404
