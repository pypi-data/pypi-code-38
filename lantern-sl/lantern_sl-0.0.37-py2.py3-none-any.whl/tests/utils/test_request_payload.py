from decimal import Decimal

RESPONSE_DATA_ORIGINAL_DICT = {
    "name": "my name",
    "results": [{"name": "name 1", "val": Decimal('25.2500')}],
    "username": "local_user",
    "lantern_desc": "My lantern desc"
}

RESPONSE_DATA_RESULT_FILTER_SYSTEM_COLS = {
    "name": "my name",
    "results": [{"name": "name 1", "val": Decimal('25.2500')}]
}

RESPONSE_DATA_RESULT_DECIMAL_TO_FLOAT = {
    "name": "my name",
    "results": [{"name": "name 1", "val": 25.25}],
    "username": "local_user",
    "lantern_desc": "My lantern desc",
}


RESPONSE_DATA_RESULT_FILTER_SYSTEM_TO_FLOAT = {
    "name": "my name",
    "results": [{"name": "name 1", "val": 25.25}],
}