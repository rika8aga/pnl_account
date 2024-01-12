import decimal
from datetime import date, datetime
from pydantic import BaseModel
from models import PaymentDirection, PaymentType


class PaymentDirectionDto(BaseModel):
    name: str
    direction: PaymentDirection
    period: datetime
    value: decimal.Decimal

    def __eq__(self, other):
        if not isinstance(other, PaymentDirectionDto):
            return NotImplemented
        return self.name == other.name and self.direction == other.direction

    def __hash__(self):
        return hash((self.name, self.direction))


class PaymentTypeDto(BaseModel):
    name: str
    direction: PaymentDirection
    payment_type: PaymentType

    # @field_validator("payment_type")
    # @classmethod
    # def validate_payment_type(cls, value):
    #     match value:
    #         case None:
    #             raise ValueError("Заполните типы платежей для всех платежей")
    #     return value


class PaymentCompanyDto(PaymentTypeDto, PaymentDirectionDto):
    company_id: int


class PaymentDto(PaymentCompanyDto):
    id: int
    company_name: str


class CompanyAddDto(BaseModel):
    name: str


class CompanyDto(CompanyAddDto):
    id: int


class CompanyPaymentDto(CompanyDto):
    payments: list['PaymentDto']


class CompanyDirectionSumDto(BaseModel):
    company: str
    direction: PaymentDirection
    period: date
    value: decimal.Decimal
