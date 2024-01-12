from datetime import date

from query import DatabaseManager
from schemas import CompanyDto
import streamlit as st


class CompanySelector:
    @staticmethod
    async def select_company() -> CompanyDto:
        companies = await DatabaseManager.get_company_names()
        with st.container(border=True):
            st.subheader('Наименование компании')
            company: CompanyDto = st.selectbox(
                label='company_name',
                label_visibility='collapsed',
                options=companies,
                format_func=lambda x: x.name
            )
        return company

    @staticmethod
    async def multiselect_company() -> list[CompanyDto]:
        companies = await DatabaseManager.get_company_names()
        with st.container(border=True):
            st.subheader('Наименование компании')
            company: list[CompanyDto] = st.multiselect(
                label='company_name',
                label_visibility='collapsed',
                options=companies,
                default=companies,
                format_func=lambda x: x.name
            )
        return company


class PeriodSelector:
    @staticmethod
    async def select_period() -> tuple[date, date]:
        default_value = await DatabaseManager.get_payments_period()
        with st.container(border=True):
            st.subheader('Период')
            period: tuple[date, date] = st.date_input(
                value=default_value,
                label='period',
                label_visibility='collapsed',
            )
            match period:
                case (start,):
                    period = (start, date.today())
        return period
