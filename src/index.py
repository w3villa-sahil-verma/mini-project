from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager


from src.database.connection import engine
from src.database.Base import Base


from src.auth.routes.Routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Application starting up...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("🛑 Application shutting down...")

app = FastAPI(
    lifespan=lifespan,
)

app.include_router(auth_router)

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Gym Management API!"}



app.include_router(router)