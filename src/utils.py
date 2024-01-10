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
