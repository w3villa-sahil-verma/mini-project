from typing import Annotated
from fastapi import Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.Database import getAsyncDbSession
from src.models.Organization import Organization;
from src.organization.schema import Organization as OrgnaizationSchema

class Controller:
    def __init__(
            self,
            db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        ):
        self.db = db
        
    async def register(self, org:OrgnaizationSchema):
        
        # 2. Create everything inside ONE transaction
        async with self.db.begin():

            organization = Organization(
                name=org.name
            )

            self.db.add(organization)

        return {
            "message" : "success",
            "data" : organization
        }

    async def getOrganization(self, id: str):
        async with self.db.begin():
            result = await self.db.execute(
                select(Organization).where(Organization.id == id)
            )
            organization = result.scalar_one_or_none()

            if organization is None:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found"
                )

        return {
            "message": "success",
            "data": organization
        }

            
        
