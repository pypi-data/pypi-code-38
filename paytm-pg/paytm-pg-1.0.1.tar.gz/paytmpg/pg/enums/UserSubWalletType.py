
# dictionary for mapping value of type to UserWalletObject
type_user_map = dict()
# dictionary for mapping value of code to UserWalletObject
code_user_map = dict()


class UserSubWalletType:

    def __init__(self, code=None, type=None):
        self.code = code
        self.type = type
        type_user_map[self.type] = self
        code_user_map[self.code] = self

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type
        type_user_map[self.type] = self

    def get_code(self):
        return self.code

    def set_code(self, code):
        self.code = code
        code_user_map[self.code] = self

    # return object of type value == arg
    @staticmethod
    def get_ppi_type(arg):
        return type_user_map[arg]

    # return object of code value == arg
    @staticmethod
    def get_ppi_code(arg):
        return code_user_map[arg]

    def __str__(self):
        return '"' + self.type + '"'

    def __repr__(self):
        return '"' + self.type + '"'


FOOD = UserSubWalletType(2, "FOOD")
GIFT = UserSubWalletType(3, "GIFT")
MULTI_PURPOSE_GIFT = UserSubWalletType(4, "MULTI_PURPOSE_GIFT")
TOLL = UserSubWalletType(6, "TOLL")
CLOSED_LOOP_WALLET = UserSubWalletType(7, "CLOSED_LOOP_WALLET")
CLOSED_LOOP_SUB_WALLET = UserSubWalletType(8, "CLOSED_LOOP_SUB_WALLET")
FUEL = UserSubWalletType(9, "FUEL")
INTERNATIONAL_FUNDS_TRANSFER = UserSubWalletType(10, "INTERNATIONAL_FUNDS_TRANSFER")
CASHBACK = UserSubWalletType(11, "CASHBACK")
GIFT_VOUCHER = UserSubWalletType(12, "GIFT_VOUCHER")
COMMUNICATION = UserSubWalletType(13, "COMMUNICATION")
