import pandas as pd
from tabulate import tabulate


# def log_dataframe(log_table, columns=('quantity', 'value', 'units')):
#     res = pd.DataFrame(columns=columns)
#     for item in log_table:
#         dicts = dict(zip(columns, item))
#         res = res.append([dicts], ignore_index=True)
# #         res = res.append([{'quantity': item[0], 'value': item[1], 'units': item[2]}], ignore_index=True)
#     return res

# def log_formatted_table(log_table, headers=None, table_format="pipe", float_fmt=".3E"):
#     if headers is None:
#         headers = ['quantity', 'value', 'units']
#     ftm_tbl = tabulate(log_table, headers, tablefmt=table_format, floatfmt=float_fmt)
#     return ftm_tbl

def log_dataframe(list_of_dicts):
    res = pd.DataFrame(list_of_dicts,
                       columns=list(list_of_dicts.keys()))
                       # columns=list(list_of_dicts[0].keys()))
    return res

def log_markdown_table(list_of_dicts, table_format="pipe", float_fmt=".3E"):
    ftm_tbl = tabulate(list_of_dicts,
                       headers='keys',
                       tablefmt=table_format,
                       floatfmt=float_fmt)
    return ftm_tbl

def log_retrieve(list_of_dicts, quantity):
    res = [d['value'] for d in list_of_dicts if d['quantity']==quantity]
    return res[0]