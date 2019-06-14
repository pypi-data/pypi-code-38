enum_currency = dict()


class EnumCurrency:

    def __init__(self, currency="INR"):
        self.currency = currency
        enum_currency[currency] = self

    def get_currency(self):
        return self.currency

    @staticmethod
    def get_enum_by_currency(currency):
        return enum_currency[currency]

    INR = "INR"
