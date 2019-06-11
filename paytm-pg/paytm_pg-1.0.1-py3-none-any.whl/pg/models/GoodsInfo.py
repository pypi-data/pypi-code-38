from paytmpg.pg.utils.stringUtil import make_string, equals


class GoodsInfo:

    def __init__(self):
        self.merchantGoodsId = None
        self.merchantShippingId = None
        self.snapshotUrl = None
        self.description = None
        self.category = None
        self.quantity = None
        self.unit = None
        self.price = None
        self.extendInfo = None

    def set_merchant_goods_id(self, merchant_goods_id):
        self.merchantGoodsId = merchant_goods_id

    def get_merchant_goods_id(self):
        return self.merchantGoodsId

    def set_merchant_shipping_id(self, merchant_shipping_id):
        self.merchantShippingId = merchant_shipping_id

    def get_merchant_shipping_id(self):
        return self.merchantShippingId

    def set_snapshot_url(self, snapshot_url):
        self.snapshotUrl = snapshot_url

    def get_snapshot_url(self):
        return self.snapshotUrl

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_category(self, category):
        self.category = category

    def get_category(self):
        return self.category

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_quantity(self):
        return self.quantity

    def set_unit(self, unit):
        self.unit = unit

    def get_unit(self):
        return self.unit

    def set_price(self, price):
        self.price = price

    def get_price(self):
        return self.price

    def set_extend_info(self, extend_info):
        self.extendInfo = extend_info

    def get_extend_info(self):
        return self.extendInfo

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)

    def __repr__(self):
        return make_string(self)
