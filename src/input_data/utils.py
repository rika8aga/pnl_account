import streamlit as st
from models import PaymentType
from .query import DatabaseManager
from schemas import CompanyDto, PaymentDto, PaymentDirectionDto, PaymentTypeDto
from streamlit.runtime.uploaded_file_manager import UploadedFile


class FileUploader:
    @staticmethod
    def upload_file() -> UploadedFile:
        with st.container(border=True):
            st.subheader('Входящий документ')
            file = st.file_uploader(
                label='Выберите документ или перетащите',
                type=['xlsx', 'xls'],
                accept_multiple_files=False
            )
        return file


class CompanySelector:
    def __init__(self):
        self.company = None

    async def select_company(self):
        companies = await DatabaseManager.get_company_names()
        with st.container(border=True):
            st.subheader('Наименование компании')
            self.company: CompanyDto = st.selectbox(
                label='company_name',
                label_visibility='collapsed',
                options=companies,
                format_func=lambda x: x.name
            )


class PaymentTypeSelector:
    def __init__(self, payments: list[PaymentDirectionDto]):
        self._payments_dto = payments
        self.payments_type = None

    DIRECTION_MAPPING = {
        'income': 'Доходы',
        'expense': 'Расходы',
        'cost': 'Себестоимость',
        'Доходы': 'income',
        'Расходы': 'expense',
        'Себестоимость': 'cost'
    }

    TYPE_MAPPING = {
        'Товар': 'product',
        'Услуга': 'service',
        'Общие': 'general',
    }

    def _get_unique_payments(self) -> list[dict[str, str]]:
        set_unique_payments = set(
            (payment.name, payment.direction.value) for payment in self._payments_dto
        )
        dict_unique_payments = [
            {
                'name': i[0],
                'direction': PaymentTypeSelector.DIRECTION_MAPPING.get(i[1]),
                'payment_type': ''
            } for i in set_unique_payments
        ]
        return dict_unique_payments

    def _data_editor(self) -> None:
        unique_payments = self._get_unique_payments()
        self.payments_type = st.data_editor(
            unique_payments,
            disabled=['name', 'direction'],
            column_config={
                'payment_type': st.column_config.SelectboxColumn(
                    label='Тип платежа',
                    help="",
                    width="medium",
                    options=('Товар', 'Услуга', 'Общие', 'Не учитывать'),
                    required=True,
                )
            },
            use_container_width=True
        )

    def _set_directions(self):
        for i in self.payments_type:
            i['direction'] = PaymentTypeSelector.DIRECTION_MAPPING.get(i['direction'])

    def _set_type(self):
        for i in self.payments_type:
            i['payment_type'] = PaymentTypeSelector.TYPE_MAPPING.get(i['payment_type'])

    def _get_payment_type_dto(self) -> list[PaymentTypeDto]:
        self._data_editor()
        self._set_directions()
        self._set_type()
        payments_type_dto = [PaymentTypeDto(**payment_type) for payment_type in self.payments_type]
        st.write(payments_type_dto)
        return payments_type_dto

    @property
    def payments_type_dto(self) -> list[PaymentTypeDto]:
        return self._get_payment_type_dto()
