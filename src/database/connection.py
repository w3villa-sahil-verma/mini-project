from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


DATABASE_URL = "mysql+pymysql://root:admin@localhost:3306/gym_management"

engine = create_async_engine(DATABASE_URL)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# FastAPI dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session