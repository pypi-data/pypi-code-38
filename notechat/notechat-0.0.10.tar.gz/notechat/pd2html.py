#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/04/16 10:34
# @Author  : niuliangtao
# @Site    : 
# @File    : pd2html.py
# @Software: PyCharm
from pyhtml import html, body, img, table, li, a, td, tr


class pd2html:
    def __init__(self, data):
        self.data = data

        self.columns = data.columns.values

    def get_title(self):
        tds = []
        for col in self.columns:
            tds.append(td(col))
        return tr(tds)

    def get_td(self, col, data):
        if col == 'itemId':
            url = "https://weidian.com/item.html?itemID=" + str(data)
            res = td(li(a(href=url, target="_blank")(data)))
        elif col == 'shopId' or col == 'sellerId':
            url = "https://weidian.com/?userid=" + str(data)
            res = td(li(a(href=url, target="_blank")(data)))
        elif ("img" in col) or ("image" in col):
            res = td(img(src=data + "?w=150&h=150&cp=1"))
        else:
            res = td(data)
        return res

    def get_tr(self, data):
        l1 = len(self.columns)
        tds = []
        for i in range(0, l1):
            tds.append(self.get_td(self.columns[i], data[i]))

        return tr(tds)

    def html(self):
        trs = [self.get_title()]
        for d in self.data.values:
            trs.append(self.get_tr(d))

        return html(body(table(trs)))

    def html_str(self):
        return self.html().render(user='Cenk')
