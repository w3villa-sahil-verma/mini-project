from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database.Database import Database;


class Application: 
    def __init__(self, name):
        self.name = name
        self.app = FastAPI(title=self.name, lifespan=self.lifespan)
        self.db = Database()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):

        print("🚀 Application starting...")

        await self.db.connect()

        await self.db.initialize_database()

        yield

        print("🛑 Application shutting down...")

        await self.db.close()

    def register_routes(self):
        pass;


APPLICATION_NAME = "Gym Management System"

application = Application(APPLICATION_NAME)

app = application.app;