from datetime import date

from sqlalchemy import select, insert, func
from database import async_session
from models import Company, Payment
from schemas import CompanyDto, PaymentCompanyDto, PaymentDto, CompanyDirectionSumDto


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
    async def insert_payments(payments: list[PaymentCompanyDto]) -> None:
        async with async_session() as session:
            stmt = insert(Payment).values([payment.model_dump() for payment in payments])
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def get_table_by_company_direction(company_id_list: list[int], period: tuple[date, date]) -> list[CompanyDirectionSumDto]:
        async with async_session() as session:
            stmt = (
                select(
                    func.json_build_object(
                        'company', Company.name,
                        'direction', Payment.direction,
                        'period', Payment.period,
                        'value', func.sum(Payment.value)
                    ).label('company')
                )
                .select_from(Company)
                .where(
                    Company.id.in_(company_id_list),
                    Payment.period >= period[0],
                    Payment.period <= period[1],
                )
                .group_by(Payment.direction, Company.name, Payment.period)
                .join(Payment, Payment.company_id == Company.id)
            )
            result = await session.execute(stmt)
            result_orm = result.scalars().all()
            print(f'Companies: {result_orm}')
            result_dto = [CompanyDirectionSumDto(**row) for row in result_orm]
            return result_dto

    @staticmethod
    async def get_payments_period() -> tuple[date, date]:
        async with async_session() as session:
            stmt = select(
                func.min(Payment.period).label('min_period'),
                func.max(Payment.period).label('max_period'),
            )
            result = await session.execute(stmt)
            result_orm = result.first()
            print(result_orm.min_period, result_orm.max_period)
            return result_orm.min_period, result_orm.max_period
