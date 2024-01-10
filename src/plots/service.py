import streamlit as st
import pandas as pd
from query import DatabaseManager
from schemas import CompanyDirectionSumDto, CompanyDto


class IncomeStatementService:
    def __init__(self, company_list: list[CompanyDto]):
        self.company_list = company_list
        self.dataframe = None

    async def get_table_by_company_direction(self) -> list[CompanyDirectionSumDto]:
        company_id_list = [company.id for company in self.company_list]
        return await DatabaseManager.get_table_by_company_direction(company_id_list)

    async def create_dataframe(self) -> pd.DataFrame:
        pivot_by_company_direction = await self.get_table_by_company_direction()
        st.write(pivot_by_company_direction)
        return pd.DataFrame([item.model_dump() for item in pivot_by_company_direction])

    async def get_pivot_table(self) -> pd.DataFrame:
        df = await self.create_dataframe()
        df['direction'] = df['direction'].apply(lambda x: x.value)
        return df.pivot(index='company', columns='direction', values='value')

    async def get_income_statement(self) -> None:
        self.dataframe = await self.get_pivot_table()
        self.dataframe['gross_profit'] = self.dataframe['income'] - self.dataframe['cost']
        self.dataframe['profit'] = self.dataframe['gross_profit'] - self.dataframe['expense']

    async def get_income_statement_to_show(self) -> pd.DataFrame:
        await self.get_income_statement()
        self.dataframe.rename(columns={'income': 'Выручка', 'cost': 'Себестоимость', 'expense': 'Расходы',
                                       'gross_profit': 'Валовая прибыль', 'profit': 'Прибыль'}, inplace=True)
        return self.dataframe
