import asyncio
import streamlit as st
from input_data.service import PaymentProcessor
from input_data.utils import FileUploader, CompanySelector, PaymentTypeSelector
from input_data.query import DatabaseManager


async def main():
    st.title('Ввод данных')
    file = FileUploader.upload_file()
    payment_processor = PaymentProcessor(file)

    company = await CompanySelector.select_company()
    payment_type_selector = PaymentTypeSelector(payment_processor.payments)
    payment_types = payment_type_selector.payments_type_dto

    if st.button('Записать'):
        payment_processor.add_type_to_payments(payment_types=payment_types, company_dto=company)
        st.write(payment_processor.payments_to_db)
        await DatabaseManager.insert_payments(payment_processor.payments_to_db)


if __name__ == '__main__':
    asyncio.run(main())
