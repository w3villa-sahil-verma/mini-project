from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.model.Account import Account


class AccountRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, account: Account) -> Account:
        self.session.add(account)

        await self.session.flush()

        return account

    async def get_by_id(self, account_id: int) -> Account | None:
        result = await self.session.execute(
            select(Account)
            .where(Account.id == account_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> Account | None:
        result = await self.session.execute(
            select(Account)
            .where(Account.user_id == user_id)
        )

        return result.scalar_one_or_none()

    async def update(self, account: Account) -> Account:
        self.session.add(account)

        await self.session.flush()

        return account

    async def delete(self, account: Account) -> None:
        await self.session.delete(account)
        await self.session.flush()