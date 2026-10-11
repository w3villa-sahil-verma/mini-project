from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

from src.database.Database import db;
from src.utils.colored_console import console;
from src.apis.v1.Routes import router;
from src.core.exceptions.exceptions import AppException
from src.core.exceptions.handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

APPLICATION_NAME = "Gym Management System"

class Application: 
    def __init__(self, name):
        self.name:str = name
        self.app: FastAPI = FastAPI(title=self.name, lifespan=self.lifespan)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):

        console.print("🚀 Application starting...", style="bold green")

        await db.connect()

        await db.initialize_database()

        yield

        console.print("🛑 Application shutting down...", style="bold red")

        await db.close()

    def registerRouter(self, router:APIRouter ):
        self.app.include_router(router)
        pass;

application = Application(APPLICATION_NAME)

application.registerRouter(router)

app = application.app;

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)