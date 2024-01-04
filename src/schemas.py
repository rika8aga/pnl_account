import decimal
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, field_validator
from models import PaymentDirection, PaymentType


class PaymentDirectionDto(BaseModel):
    name: str
    direction: PaymentDirection
    period: datetime
    value: decimal.Decimal


class PaymentTypeDto(BaseModel):
    name: str
    direction: PaymentDirection
    payment_type: PaymentType
    #
    # @field_validator("payment_type")
    # @classmethod
    # def validate_payment_type(cls, value):
    #     if not value:
    #         raise ValueError("Заполните типы платежей для всех платежей")
    #     return value


class PaymentDto(PaymentTypeDto, PaymentDirectionDto):
    id: int



class PaymentCompanyDto(PaymentDto):
    company_id: int
    company: 'CompanyDto'


class CompanyAddDto(BaseModel):
    name: str


class CompanyDto(CompanyAddDto):
    id: int


class CompanyPaymentDto(BaseModel):
    payment: list['PaymentDto']
