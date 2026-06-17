from fastapi import FastAPI

from api.summary_routes import (
    router as summary_router
)

from api.health_routes import (
    router as health_router
)

from config.settings import (
    settings
)

app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION
)

app.include_router(

    health_router,

    prefix="/api/v1",

    tags=["Health"]
)

app.include_router(

    summary_router,

    prefix="/api/v1",

    tags=["Summary"]
)


@app.get("/")
def root():

    return {

        "application":
        settings.APP_NAME,

        "version":
        settings.APP_VERSION,

        "status":
        "running"
    }