import asyncio
import streamlit as st
from input_data.service import PaymentProcessor
from input_data.utils import FileUploader, CompanySelector, PaymentTypeSelector
from input_data.query import DatabaseManager


async def main():
    st.title('Ввод данных')
    file = FileUploader.upload_file()

    payment_processor = PaymentProcessor(file)

    company_selector = CompanySelector()
    await company_selector.select_company()

    payment_type_selector = PaymentTypeSelector(payment_processor.payments)
    payment_types = payment_type_selector.payments_type_dto

    if st.button('Записать'):
        payment_processor.add_data_to_payments(
            data=payment_types,
            company_id=company_selector.company
        )
        st.dataframe(payment_processor.payments_to_db)
        # await DatabaseManager.insert_payments(payment_processor.payments_to_db)


if __name__ == '__main__':
    asyncio.run(main())
