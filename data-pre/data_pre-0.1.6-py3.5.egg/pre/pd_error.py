# coding=utf-8
"""
@author: magician
@file: excel.py
@date: 2018/12/21
"""

HCPoChecker = {
    'Order No.': str,
    'Year': int,
    'Planning Ssn': str,
    'Item Brand': str,
    'Transportation Method': str,
    'Payment Terms': str,
    'Payment Currency': str,
    'Order Plan Number': int,
    'Item Code': str,
    'Contracted ETD': 'datetime',
    'ETA WH': 'datetime',
    'Management Factory Code': str,
    'Management Factory': str,
    'Branch Factory Code': str,
    'Branch Factory': str,
    'Color Code': int,
    'Color': str,
    'Size Code': int,
    'Size': str,
    'SKU Code': int,
    'Sample Code': str,
    'Order Qty(pcs)': int
}

checker = {
    'hc_po': HCPoChecker
}
