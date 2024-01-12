import decimal
from datetime import date
import streamlit as st
import pandas as pd
from plotly.graph_objs import Figure
from constants import Mapping
from query import DatabaseManager
from schemas import CompanyDirectionSumDto, CompanyDto
import plotly.express as px


class IncomeStatementService:
    def __init__(self, company_list: list[CompanyDto], period: tuple[date, date]):
        self.period = period
        self.company_list = company_list
        self._dataframe = None
        self.pivot_dataframe = None
        self.shown_table = None

    async def _get_table_by_company_direction(self) -> list[CompanyDirectionSumDto]:
        company_id_list = [company.id for company in self.company_list]
        return await DatabaseManager.get_table_by_company_direction(company_id_list, self.period)

    async def _create_dataframe(self) -> pd.DataFrame:
        company_direction_dto_list = await self._get_table_by_company_direction()
        self._dataframe = pd.DataFrame([item.model_dump() for item in company_direction_dto_list])
        return self._dataframe

    async def _get_pivot_table(self) -> pd.DataFrame:
        await self._create_dataframe()
        self._dataframe['direction'] = self._dataframe['direction'].apply(lambda x: x.value)
        self.pivot_table: pd.DataFrame = self._dataframe.pivot_table(
            index='period',
            columns='direction',
            values='value',
            aggfunc='sum',
        )
        return self.pivot_table

    async def _get_income_statement(self) -> None:
        await self._get_pivot_table()
        self.pivot_table['gross_profit'] = self.pivot_table['income'] - self.pivot_table['cost']
        self.pivot_table['profit'] = self.pivot_table['gross_profit'] - self.pivot_table['expense']

    async def _format_shown_table(self) -> None:
        def format_func(x: decimal.Decimal):
            if len(str(x)) <= 10:
                return f'₸ {x:>30,.0f}'.replace(',', ' ')
            else:
                return f'₸{x:>30,.0f}'.replace(',', ' ')

        self.shown_table = self.shown_table.map(format_func)

    async def _deep_copy_pivot_table(self) -> pd.DataFrame:
        return self.pivot_table.copy(deep=True)

    async def _add_total_row(self) -> None:
        self.shown_table.loc['total'] = self.shown_table.sum(axis=0)

    async def _rename_shown_table(self) -> None:
        self.shown_table.rename(columns=Mapping.DIRECTION_MAPPING, index={'total': 'Итого'}, inplace=True)

    async def _transpose_shown_table(self) -> None:
        self.shown_table = self.shown_table.transpose()

    async def get_income_statement_to_show(self) -> None:
        await self._get_income_statement()
        self.shown_table: pd.DataFrame = await self._deep_copy_pivot_table()
        await self._add_total_row()
        await self._rename_shown_table()
        await self._format_shown_table()
        await self._transpose_shown_table()


class IncomeStatementTable:
    @staticmethod
    async def show_overall_income_statement(overall_income_statement_table_to_show: pd.DataFrame) -> None:
        st.dataframe(
            overall_income_statement_table_to_show,
            column_config={
                'direction': '',
                'Итого': st.column_config.Column(
                    width='large'
                )
            },
            use_container_width=True,
            # column_order=['Итого']
        )


class IncomeStatementPlot:
    @staticmethod
    async def show_overall_plot(df: pd.DataFrame) -> Figure:
        fig = px.ecdf(
            df,
            x=df.index,
            y=df.columns,
            # color=df.columns,
            title='Общая динамика',
            labels={
                'value': '₸',
                'variable': 'Направление',
                'index': 'Период',
            }
        )
        st.plotly_chart(fig)

