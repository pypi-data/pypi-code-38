#-*- coding: utf-8 -*-
"""
Author  : Jiwoo Park
Date    : 2019. 1. 21
Desc    : Record of transaction
"""
from datetime import datetime

class Record():
    """
    Single Transaction Record
    Attributes 1. date of transaction
               2. amounts of stocks
    Methods    1. evaluation
    """
    def __init__(self, date, assets):
        """
        :param date:    Date that quant record
        :param assets:  Asset and it amount that quant wants to buy
        """
        self.date = date
        self.assets = assets


    def __str__(self):
        repr_str = "\n" \
                   "{:>15} | Amount\n" \
                   "=========================\n"\

        for code, name, amount in self.assets:
            name = (name[:4] + '..') if len(name) > 4 else name
            repr_str += "{:>8}({:<6})| {:>6}\n".format(code, name, amount)

        return repr_str.format(self.date.strftime("%Y-%m-%d"), self.assets, 3)


    def evaluate(self):
        self.purchase_unit_price = None
        self.current_price = None

if __name__ == "__main__":
    sample_asset = [("A000030", "갑돌이", 3), ("A000050", "asdfdsdf갑을병정sdfsdfsdf컴퍼니", 500)]
    rcd = Record(datetime(2019, 1, 3), sample_asset)
    print(rcd)

