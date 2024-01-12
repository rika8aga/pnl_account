class Mapping:
    DIRECTION_MAPPING = {
        'income': 'Доходы',
        'expense': 'Расходы',
        'cost': 'Себестоимость',
        'Доходы': 'income',
        'Расходы': 'expense',
        'Себестоимость': 'cost',
        'gross_profit': 'Валовая прибыль',
        'profit': 'Прибыль',
    }

    TYPE_MAPPING = {
        'product': 'Товар',
        'service': 'Услуга',
        'general': 'Общие',
        'Товар': 'product',
        'Услуга': 'service',
        'Общие': 'general',
        'Не учитывать': 'drop'
    }
