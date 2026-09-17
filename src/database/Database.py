from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.database.Base import Base


class Database:
    def __init__(self):
        DATABASE_USER = "root"
        DATABASE_PASSWORD = "admin"
        DATABASE_HOST = "localhost"
        DATABASE_PORT = "3306"
        DATABASE_NAME = "gym_management"
        DATABASE_DRIVER = "mysql+aiomysql"

        self.DATABASE_NAME = DATABASE_NAME

        # URL WITHOUT database name
        self.DATABASE_URL = (
            f"{DATABASE_DRIVER}://"
            f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
            f"{DATABASE_HOST}:{DATABASE_PORT}"
        )
        self.DATABASE_URL_WITH_DB = (
            f"{DATABASE_DRIVER}://"
            f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
            f"{DATABASE_HOST}:{DATABASE_PORT}/"
            f"{DATABASE_NAME}"
        )

        self.engine: AsyncEngine | None = None
        self.AsyncSessionLocal: async_sessionmaker | None = None

    async def connect(self):
        self.engine = create_async_engine(
            self.DATABASE_URL,
            echo=True,
        )

    async def initialize_database(self):

        if not self.engine:
            raise Exception("Database engine is not initialized. Call connect() first.")

        # 1. Create database
        async with self.engine.begin() as conn:
            await conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS "
                    f"`{self.DATABASE_NAME}`"
                )
            )

        # 2. Close the server-level engine
        await self.engine.dispose()

        self.engine = create_async_engine(
            self.DATABASE_URL_WITH_DB,
            echo=True,
        )

        # 4. Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.create_all
            )

        # 5. Create session factory
        self.AsyncSessionLocal: async_sessionmaker | None = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def getAsyncSession(self):
        if not self.AsyncSessionLocal:
            raise Exception("Session factory is not initialized. Call initialize_database() first.")
        
        return self.AsyncSessionLocal()

    async def close(self):
        if self.engine:
            await self.engine.dispose()


db = Database();

async def getAsyncDbSession():
    session = await db.getAsyncSession()

    try:
        yield session
    finally:
        await session.close()