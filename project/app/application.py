from app.api.metadata import description, tags_metadata
from app.api.routes import router as api_router
from app.core import config
from app.errors.api_errors import add_exception_handlers
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def create_application():
    app = FastAPI(
        title=config.PROJECT_NAME,
        version=config.VERSION,
        description=description,
        openapi_tags=tags_metadata,
    )

    app.include_router(api_router)
    add_exception_handlers(app)

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return app
