class Survey:
    name = ''
    guid = ''
    visibility = 1
    optimized_retrieval = ''
    datasets = []

class Dataset:
    name = ''
    guid = ''
    visibility = 1
    tables = []

class Table:
    name = ''
    guid = ''
    visibility_map = 1
    visibility_report = 1
    variables = []

class Variables:
    name = ''
    guid = ''
    formula = ''
    values = []