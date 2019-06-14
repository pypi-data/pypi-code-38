from paytmpg.pg.utils.stringUtil import make_string, equals


class Money:

    def __init__(self, currency, value):
        self.currency = currency
        self.value = value

    def set_currency(self, currency):
        self.currency = currency

    def set_value(self, value):
        self.value = value

    def get_curency(self):
        return self.currency

    def get_value(self):
        return self.value

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)
