# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


class PriceQuantityAmountCalMixin(object):
    def cal_amount(self):
        self.amount = self.unit_price * self.quantity
        self.amount_taxed = self.unit_price_taxed * self.quantity

    def save(self, **kwargs):
        self.cal_amount()
        super(PriceQuantityAmountCalMixin, self).save(**kwargs)


class DeliverySplitMixin(object):
    def save(self, **kwargs):
        from . import helper
        if self.delivery:
            self.delivery = self.delivery.upper().strip()
            self.delivery_days_from, self.delivery_days_to = helper.split_delivery_days(self.delivery)
        super(DeliverySplitMixin, self).save(**kwargs)
