from paytmpg.pg.utils.stringUtil import make_string, equals


class ExtendInfo:

    def __init__(self):
        self.udf1 = None
        self.udf2 = None
        self.udf3 = None
        self.mercUnqRef = None
        self.comments = None
        self.amountToBeRefunded = None
        self.subwalletAmount = None

    def set_udf1(self, udf1):
        self.udf1 = udf1

    def get_udf1(self):
        return self.udf1

    def set_udf2(self, udf2):
        self.udf2 = udf2

    def get_udf2(self):
        return self.udf2

    def set_udf3(self, udf3):
        self.udf3 = udf3

    def get_udf3(self):
        return self.udf3

    def set_merc_unq_ref(self, merc_unq_ref):
        self.mercUnqRef = merc_unq_ref

    def get_merc_unq_ref(self):
        return self.mercUnqRef

    def set_comments(self, comments):
        self.comments = comments

    def get_comments(self):
        return self.comments

    def set_amount_to_be_refunded(self, amount_to_be_refunded):
        self.amountToBeRefunded = amount_to_be_refunded

    def get_amount_to_be_refunded(self):
        return self.amountToBeRefunded

    def set_sub_wallet_amount(self, sub_wallet_amount):
        self.subwalletAmount = str()
        is_first = True
        for k, v in sub_wallet_amount.items():
            if not is_first:
                self.subwalletAmount += ','
            self.subwalletAmount += '"{}":"{}"'.format(k, v)
            is_first = False
        if is_first:
            self.subwalletAmount = None
        else:
            self.subwalletAmount = '{' + self.subwalletAmount + '}'

    def get_sub_wallet_amount(self):
        return self.subwalletAmount

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)
