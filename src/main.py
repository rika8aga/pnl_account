import asyncio
import pandas as pd
import streamlit as st
from plots.service import IncomeStatementService, IncomeStatementPlot, IncomeStatementTable
from query import DatabaseManager
from utils import CompanySelector, PeriodSelector

st.set_page_config(
    page_title='Отчет о прибылях и убытках',
    page_icon=':moneybag:',
    initial_sidebar_state='collapsed',
)
st.title('Отчет о прибылях и убытках')


async def main():
    companies = await CompanySelector.multiselect_company()
    period = await PeriodSelector.select_period()
    income_statement = IncomeStatementService(companies, period)
    await income_statement.get_income_statement_to_show()
    await IncomeStatementTable.show_overall_income_statement(income_statement.shown_table)
    st.dataframe(income_statement.pivot_table)
    await IncomeStatementPlot.show_overall_plot(income_statement.pivot_table)
    if st.button('Download'):
        pass


if __name__ == '__main__':
    asyncio.run(main())
