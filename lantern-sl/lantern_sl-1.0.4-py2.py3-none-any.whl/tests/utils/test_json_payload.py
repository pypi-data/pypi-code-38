from decimal import Decimal


FLOATS_SIMPLE = {
    'number1': 12312.2, 
    'number2': 1}

DECIMALS_SIMPLE = {
    'number1': Decimal('12312.2000'), 
    'number2': 1}



FLOATS_LIST_1 = {
    'numbers': [
        {'num1': 123123.23}, 
        {'num2': 12313.2123}
    ], 
    'num2': 1, 
    'num3': 123123.23}

DECIMALS_LIST_1 = {
    'numbers': [
        {'num1': Decimal('123123.2300')}, 
        {'num2': Decimal('12313.2123')}
    ], 
    'num2': 1, 
    'num3': Decimal('123123.2300')}



FLOATS_LIST_2 = {
    'numbers': [
        {'num1': 123123.23}, 
        {'num2': 12313.2123}, 
        {'childs': [
            {'num1': 123123.23}, 
            {'num2': 12313.2123}
        ]}
    ], 
    'num2': 1, 
    'num3': 123123.23}

DECIMALS_LIST_2 = {
    'numbers': [
        {'num1': Decimal('123123.2300')}, 
        {'num2': Decimal('12313.2123')}, 
        {'childs': [
            {'num1': Decimal('123123.2300')}, 
            {'num2': Decimal('12313.2123')}
        ]}
    ], 
    'num2': 1, 
    'num3': Decimal('123123.2300')}



FLOATS_LIST_3 = {
    'list1': [
        [{'num1': 12312.2}],
        [{'num2': 3}],
    ],
    'num2': 1}

DECIMALS_LIST_3 = {
    'list1': [
        [{'num1': Decimal('12312.2000')}],
        [{'num2': 3}],
    ],
    'num2': 1}