
NUEVO = "nuevo"
HISTORICO = "histórico"

class Collection:

    def __init__(self, document, raw_code, customer, date, amount, errors):
        collection = dict()

        # xubio transaction
        self.document = document
        self.raw_code = raw_code or ""

        # customer
        self.customer = customer

        # transaction details
        self.date = date
        self.amount = amount

        # defaults
        self.version = HISTORICO
        self.sales_order = ""
        self.payments = ""

        if "-" in raw_code:
            self.version = NUEVO
            order_and_payments = raw_code.split("-")
            self.sales_order, *self.payments = order_and_payments

        if self.sales_order and len(self.sales_order) != 5:
            error = "Cobranza con orden de compra errónea (%s). Documento: %s" % (self.sales_order, self.document)
            errors.append(error)

    def to_dict(self):
        collection = {}

        collection['version'] = self.version
        collection['date'] = self.date
        collection['customer'] = self.customer
        collection['amount'] = self.amount
        collection['sales_order'] = self.sales_order
        collection['payments'] = self.payments

        return collection