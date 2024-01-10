import pandas as pd
import streamlit as st
from pydantic import ValidationError
from constants import Mapping
from schemas import PaymentDirectionDto, PaymentTypeDto
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


class PaymentTypeSelector:
    def __init__(self, payments: list[PaymentDirectionDto]):
        self._payments_dto = payments
        self.payments_type = None

    def _get_unique_payments(self) -> pd.DataFrame:
        unique_payments_type = pd.DataFrame([item.model_dump() for item in list(set(self._payments_dto))])
        unique_payments_type['payment_type'] = None
        unique_payments_type['direction'] = unique_payments_type['direction'].apply(
            lambda x: Mapping.DIRECTION_MAPPING.get(x.value)
        )
        unique_payments_type = unique_payments_type.drop(columns=['value', 'period'])
        return unique_payments_type

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
        self.payments_type['direction'] = self.payments_type['direction'].apply(
            lambda x: Mapping.DIRECTION_MAPPING.get(x)
        )

    def _set_type(self):
        self.payments_type['payment_type'] = self.payments_type['payment_type'].apply(
            lambda x: Mapping.TYPE_MAPPING.get(x)
        )

    def _drop_none_payment_type(self):
        self.payments_type.query('payment_type != "drop"', inplace=True)

    def _get_payment_type_dto(self) -> list[PaymentTypeDto]:
        self._data_editor()
        self._set_directions()
        self._set_type()
        self._drop_none_payment_type()
        try:
            payments_type_dto = [PaymentTypeDto(**payment_type) for payment_type in self.payments_type.to_dict('records')]
            return payments_type_dto
        except ValidationError as e:
            if e.errors()[0]['loc'] == ('payment_type',):
                st.warning('Заполните типы платежей для всех платежей')
                st.stop()

    @property
    def payments_type_dto(self) -> list[PaymentTypeDto]:
        return self._get_payment_type_dto()
