from fastapi import FastAPI

import uvicorn

from auth.views import router as auth_router
from core.settings import settings

app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
