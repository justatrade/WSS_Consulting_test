from fastapi import FastAPI

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.tickets import router as tickets_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.project_name,
    docs_url="/swagger",
    redoc_url="/docs",
)
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
