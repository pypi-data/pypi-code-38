# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Sum

from . import choices, mixins
from django_szuprefix_saas.saas.models import Party
from django_szuprefix.utils.modelutils import CodeMixin


class Manufacturer(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "品牌"
        permissions = (
            ("view_all_manufacturer", "查看所有品牌"),
        )
        ordering = ('-create_time',)
        unique_together = ('party', 'name')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_manufacturers",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.name


class Company(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "公司"
        permissions = (
            ("view_all_company", "查看所有公司"),
        )
        unique_together = ('party', 'name')
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_vendors",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    is_vendor = models.BooleanField("是供应商", blank=True, default=False)
    is_customer = models.BooleanField("是客户", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.name


class Product(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "产品"
        permissions = (
            ("view_all_product", "查看所有产品"),
        )
        ordering = ('-create_time',) #('manufacturer', 'name')
        unique_together = ('party', 'manufacturer', 'name', 'number')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_products",
                              on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=Manufacturer._meta.verbose_name, null=True, blank=True,
                                     related_name="products", on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    number = models.CharField("型号", max_length=255)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s" % (self.manufacturer, self.name, self.number)


class Request(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "询价"
        ordering = ('-create_time',)
        permissions = (
            ("view_all_request", "查看所有询价"),
        )
        unique_together = ('party', 'code')

    code = models.CharField("单号", max_length=64, blank=True, default="")
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_requests",
                              on_delete=models.PROTECT)

    user = models.ForeignKey(User, verbose_name="人员", null=True, related_name="quote_requests",
                             on_delete=models.PROTECT)
    customer = models.ForeignKey(Company, verbose_name='客户', related_name="requests",
                                 on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField("状态", choices=choices.CHOICES_REQUEST_STATUS, null=True,
                                              default=choices.REQUEST_STATUS_REQUEST)
    amount = models.DecimalField("未税金额", decimal_places=2, max_digits=10, default=0)
    amount_taxed = models.DecimalField("含税金额", decimal_places=2, max_digits=10, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s 于 %s 询价" % (self.customer, self.create_time.strftime("%Y%m%d"))

    def gen_code(self):
        from datetime import date
        d = date.today()  # .strftime("%Y%M%d")
        c = self.party.quote_requests.filter(create_time__gte=d).count() + 1
        return "QR%s%03d" % (d.strftime("%Y%m%d"), c)

    def save(self, **kwargs):
        if not self.code:
            self.code = self.gen_code()
        if self.status is None:
            self.status = choices.REQUEST_STATUS_REQUEST
        return super(Request, self).save(**kwargs)

    def cal_amount(self):
        from django.db.models import Sum
        self.amount = self.items.filter(is_valid=True).aggregate(amount=Sum("amount"))['amount']
        self.amount_taxed = self.items.filter(is_valid=True).aggregate(amount_taxed=Sum("amount_taxed"))['amount_taxed']
        # print self.amount_taxed, self.amount


class Item(mixins.PriceQuantityAmountCalMixin, mixins.DeliverySplitMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "询价项目"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_items",
                              on_delete=models.PROTECT)
    request = models.ForeignKey(Request, verbose_name=Request._meta.verbose_name, related_name="items",
                                on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=Product._meta.verbose_name, related_name="items",
                                on_delete=models.PROTECT)
    customer = models.ForeignKey(Company, verbose_name='客户', related_name="items",
                                 blank=True, null=True, on_delete=models.PROTECT)
    # unit = models.CharField("单位", max_length=16, blank=True, default="PCS")
    quantity = models.PositiveIntegerField("数量")
    amount = models.DecimalField("未税金额", decimal_places=2, max_digits=10, default=0)
    amount_taxed = models.DecimalField("含税金额", decimal_places=2, max_digits=10, default=0)
    unit_price = models.DecimalField("未税单价", decimal_places=2, null=True, blank=True, max_digits=10)
    unit_price_taxed = models.DecimalField("含税单价", decimal_places=2, null=True, blank=True, max_digits=10)
    delivery = models.CharField("货期", max_length=32, null=True, blank=True)
    delivery_days_from = models.PositiveIntegerField("货期最短天数", null=True, blank=True)
    delivery_days_to = models.PositiveIntegerField("货期最长天数", null=True, blank=True)
    memo = models.TextField("备注", blank=True, default="")
    is_valid = models.BooleanField("有效", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s by %s : %s" % (self.product, self.request, self.unit_price)

    def save(self, **kwargs):
        if self.unit_price is None:
            self.unit_price = 0
        if self.unit_price_taxed is None:
            self.unit_price_taxed = 0
        self.customer = self.request.customer
        return super(Item, self).save(**kwargs)


class Quote(mixins.DeliverySplitMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "报价"
        permissions = (
            ("view_all_quote", "查看所有报价"),
        )
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_quotes",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="人员", null=True, related_name="quote_quotes",
                             on_delete=models.PROTECT)
    vendor = models.ForeignKey(Company, verbose_name='供应商', related_name="quotes",
                               on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=Product._meta.verbose_name, related_name="quotes",
                                null=True, on_delete=models.PROTECT)
    # unit = models.CharField("单位", max_length=16, blank=True, default="件")
    # quantity = models.PositiveIntegerField("数量", default=0)
    # amount = models.DecimalField("未税金额", decimal_places=2, max_digits=10, default=0)
    # amount_taxed = models.DecimalField("含税金额", decimal_places=2, max_digits=10, default=0)
    unit_price = models.DecimalField("未税单价", decimal_places=2, max_digits=10)
    unit_price_taxed = models.DecimalField("含税单价", decimal_places=2, max_digits=10)
    delivery = models.CharField("货期", max_length=32)
    delivery_days_from = models.PositiveIntegerField("货期最短天数", blank=True, default=0)
    delivery_days_to = models.PositiveIntegerField("货期最长天数", blank=True, default=0)
    is_valid = models.BooleanField("有效", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s by %s" % (self.product, self.vendor)

    
    def save(self, **kwargs):
        # if not self.unit:
        #     self.unit = "PCS"
        return super(Quote, self).save(**kwargs)