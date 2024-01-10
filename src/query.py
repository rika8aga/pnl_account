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
    async def get_payment_for_net_income_2():
        async with async_session() as session:
            stmt = (
                select(
                    Payment.id,
                    Payment.name,
                    Payment.direction,
                    Payment.value,
                    Payment.period,
                    Payment.payment_type,
                    Company.id.label('company_id'),
                    Company.name.label('company_name'),
                )
                .join(Company, Payment.company_id == Company.id)
            )
            result = await session.execute(stmt)
            print(f'result: {result.all()}')
            result_dto = [PaymentDto.model_validate(row, from_attributes=True) for row in result.all()]
            print(f'result_dto: {result_dto}')
            return result_dto

    @staticmethod
    async def get_table_by_company_direction(company_id_list: list[int]) -> list[CompanyDirectionSumDto]:
        async with async_session() as session:
            stmt = (
                select(
                    func.json_build_object(
                        'company', Company.name,
                        'direction', Payment.direction,
                        'value', func.sum(Payment.value)
                    ).label('company')
                )
                .select_from(Company)
                .where(Company.id.in_(company_id_list))
                .group_by(Payment.direction, Company.name)
                .join(Payment, Payment.company_id == Company.id)
            )
            result = await session.execute(stmt)
            result_orm = result.scalars().all()
            print(f'Companies: {result_orm}')
            result_dto = [CompanyDirectionSumDto(**row) for row in result_orm]
            return result_dto
