import asyncio
import pandas as pd
import streamlit as st
from plots.service import IncomeStatementService
from query import DatabaseManager
from utils import CompanySelector

st.title('Отчет о прибылях и убытках')


async def main():
    companies = await CompanySelector.multiselect_company()
    income_statement = IncomeStatementService(companies)
    await income_statement.get_income_statement()
    st.dataframe(income_statement.dataframe)
    if st.button('Download'):
        pass


if __name__ == '__main__':
    asyncio.run(main())
