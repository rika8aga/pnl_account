from sqlalchemy import ForeignKey, Numeric, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase
from enum import Enum


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = 'company'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    payments: Mapped[list['Payment']] = relationship(back_populates='company')


class PaymentType(Enum):
    product = 'product'
    service = 'service'
    general = 'general'


class PaymentDirection(Enum):
    income = 'income'
    expense = 'expense'
    cost = 'cost'


class Payment(Base):
    __tablename__ = 'payment'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    payment_type: Mapped[PaymentType]
    direction: Mapped[PaymentDirection]
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='payments')
    period: Mapped[Date] = mapped_column(Date)
    value: Mapped[Numeric] = mapped_column(Numeric(precision=13, scale=3, asdecimal=True))
