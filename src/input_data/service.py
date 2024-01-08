from abc import ABC, abstractmethod
import pandas as pd
from pydantic import ValidationError
from streamlit.runtime.uploaded_file_manager import UploadedFile
from models import PaymentDirection
from datetime import datetime, date
from schemas import PaymentType, PaymentTypeDto, PaymentDto, PaymentDirectionDto, CompanyDto, PaymentCompanyDto
import streamlit as st


class FileReaderBase(ABC):
    @abstractmethod
    def get_dataframe(self, file: UploadedFile) -> pd.DataFrame:
        pass


class ExcelFileReader(FileReaderBase):
    def get_dataframe(self, file: UploadedFile, skip_rows: int = 36) -> pd.DataFrame:
        df = pd.read_excel(file, skiprows=skip_rows)
        df.dropna(subset='Вид', axis=0, inplace=True, ignore_index=True)
        df.drop(columns=[i for i in df.columns if any(j in i for j in ('Unnamed', 'Итого'))], inplace=True)
        return df


class NoneFileReader(FileReaderBase):
    def get_dataframe(self, file: None) -> pd.DataFrame:
        return pd.DataFrame()


class PaymentProcessor:
    def __init__(self, file: UploadedFile):
        self.df: pd.DataFrame = self._read_excel(file)
        self.melted_df = None

    FILE_HANDLER = {
        None: NoneFileReader(),
        UploadedFile: ExcelFileReader()
    }

    DIRECTION_HANDLER = {
        'income': ['income', '`Вид` == `Вид`'],
        'expense': ['expense', 'not `Вид`.str.contains("Себестоимость")'],
        'cost': ['expense', '`Вид`.str.contains("Себестоимость")']
    }

    DIRECTION_MAPPING = {
        'income': 'Доходы',
        'expense': 'Расходы',
        'cost': 'Себестоимость'
    }

    MONTH_MAPPING = {
        'янв.': 1,
        'февр.': 2,
        'март': 3,
        'апр.': 4,
        'май': 5,
        'июнь': 6,
        'июль': 7,
        'авг.': 8,
        'сент.': 9,
    }

    def _read_excel(self, file: UploadedFile | None) -> pd.DataFrame:
        file_reader = (self.FILE_HANDLER.get(type(file), NoneFileReader()))
        return file_reader.get_dataframe(file)

    def _get_indexes(self) -> dict[str, tuple]:
        income_index = self.df[self.df['Вид'] == 'Доходы без НДС'].index[0]
        expense_index = self.df[self.df['Вид'] == 'Расходы'].index[0]
        return {
            'income_index': (income_index + 1, expense_index),
            'expense_index': (expense_index + 1, len(self.df) - 1)
        }

    def _get_dict_data(self) -> dict[str, pd.DataFrame]:
        indexes = self._get_indexes()
        return {
            'income': self.df.iloc[slice(*indexes['income_index'])],
            'expense': self.df.iloc[slice(*indexes['expense_index'])]
        }

    def _set_date_format(self):
        def get_date_format(date_string: str | pd.Timestamp) -> datetime | pd.Timestamp:
            match date_string:
                case str(value):
                    month_name, year = value.split(' ')
                    month_number = PaymentProcessor.MONTH_MAPPING.get(month_name)
                    return datetime.strptime(f'{month_number}.{year}', '%m.%y')
                case pd.Timestamp():
                    return date_string

        self.melted_df['period'] = self.melted_df['period'].apply(get_date_format)

    def _get_melted_df(self) -> str:
        if not self.df.empty:
            dict_data = self._get_dict_data()
            for direction in PaymentDirection:
                data_dir, query = self.DIRECTION_HANDLER.get(direction.value)
                data = dict_data[data_dir].query(query)
                data = pd.melt(
                    data,
                    id_vars='Вид',
                    value_vars=data.columns.drop('Вид'),
                    var_name='period',
                    value_name='value'
                ).rename(columns={'Вид': 'name'})
                data['direction'] = direction
                self.melted_df = pd.concat([self.melted_df, data], axis=0, ignore_index=True).fillna(0)
        else:
            self.melted_df = pd.DataFrame([{
                "name": "",
                "period": pd.Timestamp(date.today()),
                "value": 0,
                "direction": PaymentDirection.income,
            }])
        self._set_date_format()
        return f'{len(self.melted_df)}'

    def _get_payments(self) -> list[PaymentDirectionDto]:
        self._get_melted_df()
        # st.dataframe(self.melted_df)
        payments_dto = [PaymentDirectionDto(**payment) for payment in self.melted_df.to_dict('records')]
        return payments_dto

    @property
    def payments(self):
        return self._get_payments()

    def _add_company(self, company_dto: CompanyDto):
        self.melted_df['company_id'] = company_dto.id

    def add_type_to_payments(self, payment_types: list[PaymentTypeDto], company_dto: CompanyDto) -> None:
        payments_type = pd.DataFrame([item.model_dump() for item in payment_types])
        # st.write(payments_type)
        self._add_company(company_dto)
        self.melted_df = self.melted_df.merge(payments_type, on=['name', 'direction'], how='left')

    def _get_payments_to_db(self) -> list[PaymentCompanyDto]:
        try:
            payments_type_dto = [PaymentCompanyDto(**payment) for payment in self.melted_df.to_dict('records')]
            return payments_type_dto
        except ValidationError as e:
            st.write(e.errors())

    @property
    def payments_to_db(self):
        return self._get_payments_to_db()
