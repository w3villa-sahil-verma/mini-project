from sqlalchemy import text
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.database.Base import Base
from src.core.settings import settings


class Database:
    def __init__(self):
        self.DATABASE_NAME = settings.DATABASE_NAME

        # URL WITHOUT database name
        self.DATABASE_URL = (
            f"{settings.DATABASE_DRIVER}://"
            f"{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@"
            f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}"
        )
        self.DATABASE_URL_WITH_DB = (
            f"{settings.DATABASE_DRIVER}://"
            f"{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@"
            f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/"
            f"{settings.DATABASE_NAME}"
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
            image_asset_columns = await conn.run_sync(
                lambda sync_conn: {
                    column["name"]
                    for column in inspect(sync_conn).get_columns("image_assets")
                }
            )
            if "is_gallery" not in image_asset_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE image_assets "
                        "ADD COLUMN is_gallery BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
            if "is_premium" not in image_asset_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE image_assets "
                        "ADD COLUMN is_premium BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
            image_asset_indexes = await conn.run_sync(
                lambda sync_conn: {
                    index["name"]
                    for index in inspect(sync_conn).get_indexes("image_assets")
                }
            )
            if "ix_image_assets_is_gallery" not in image_asset_indexes:
                await conn.execute(
                    text(
                        "CREATE INDEX ix_image_assets_is_gallery "
                        "ON image_assets (is_gallery)"
                    )
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