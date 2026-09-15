from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

from src.database.Database import Database;
from src.apis.v1.Routes import router;

APPLICATION_NAME = "Gym Management System"

class Application: 
    def __init__(self, name):
        self.name:str = name
        self.app: FastAPI = FastAPI(title=self.name, lifespan=self.lifespan)
        self.db: Database = Database()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):

        print("🚀 Application starting...")

        await self.db.connect()

        await self.db.initialize_database()

        yield

        print("🛑 Application shutting down...")

        await self.db.close()

    def registerRouter(self, router:APIRouter ):
        self.app.include_router(router)
        pass;



application = Application(APPLICATION_NAME)

application.registerRouter(router)

app = application.app;