from app.api.metadata import description, tags_metadata
from app.api.routes import router as api_router
from app.core import config
from app.errors.api_errors import add_exception_handlers
from fastapi import FastAPI


def create_application():
    app = FastAPI(
        title=config.PROJECT_NAME,
        version=config.VERSION,
        description=description,
        openapi_tags=tags_metadata,
    )

    app.include_router(api_router)
    add_exception_handlers(app)

    return app
