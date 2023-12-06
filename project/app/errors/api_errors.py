from string import Template
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIException(Exception):
    def __init__(self, http_code: int, error: str):
        self.http_code = http_code
        self.error = error


class APIExceptionBuilder:
    def __init__(self, http_code: int, message_template: str):
        self._http_code = http_code
        self._message_template = Template(message_template)

    def build(self, http_code_override: Optional[int] = None, **kwargs) -> APIException:
        return APIException(
            http_code_override or self._http_code,
            self._message_template.substitute(**kwargs),
        )


E_GENERIC_ERROR = APIExceptionBuilder(
    status.HTTP_400_BAD_REQUEST,
    "Ошибка обработки запроса: ${detail}",
)
E_ABSENT_DATA = APIExceptionBuilder(
    status.HTTP_400_BAD_REQUEST,
    "Не указан обязательный параметр ${name}: ${code}",
)
E_INVALID_DATA = APIExceptionBuilder(
    status.HTTP_400_BAD_REQUEST,
    "Некорректное значение входного параметра ${name} ${code}: ${detail}",
)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_code,
        content=dict(
            error=exc.error,
        ),
    )


async def api_request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    result = []
    for err in exc.errors():
        err_class = err["type"].split(".", 1)[0]
        if err["loc"][0] == "body" and err["type"] == "value_error.missing":
            result.append(
                E_ABSENT_DATA.build(name="/".join(err["loc"][1:]), code="UNKNOWN")
            )
        elif err["loc"][0] == "body" and err_class == "type_error":
            result.append(
                E_INVALID_DATA.build(
                    name="/".join(err["loc"][1:]), code="UNKNOWN", detail=err["msg"]
                )
            )
        else:
            result.append(
                E_GENERIC_ERROR.build(
                    http_code_override=status.HTTP_400_BAD_REQUEST,
                    detail="Некорректный параметр запроса: {}".format(err["msg"]),
                )
            )

    return await api_exception_handler(request, result[0])


def add_exception_handlers(app: FastAPI) -> None:
    for exc, callable in (
        (APIException, api_exception_handler),
        (RequestValidationError, api_request_validation_error_handler),
    ):
        app.add_exception_handler(exc, callable)
