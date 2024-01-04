from datetime import datetime
from sqlalchemy import select, insert
from database import async_session
from models import Company, Payment
from schemas import CompanyDto


class DatabaseManager:
    @staticmethod
    async def get_company_names() -> list[CompanyDto]:
        async with async_session() as session:
            stmt = select(Company)
            result = await session.execute(stmt)
            companies = result.scalars().all()
            companies = [CompanyDto.model_validate(row, from_attributes=True) for row in companies]
            return companies

    @staticmethod
    async def insert_payments(payments: list[dict]) -> None:
        async with async_session() as session:
            stmt = insert(Payment).values(payments)
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def get_payments(period: list[datetime, datetime]) -> list[dict]:
        pass
