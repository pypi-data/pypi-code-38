from paytmpg.pg.response.BaseResponseBody import BaseResponseBody
from paytmpg.pg.utils.stringUtil import make_string, equals


class InitiateTransactionResponseBody(BaseResponseBody):

    def __init__(self):
        super(InitiateTransactionResponseBody, self).__init__()
        self.txnToken = None
        self.isPromoCodeValid = None
        self.authenticated = None
        self.callbackUrl = None

    def set_txn_token(self, txn_token):
        self.txnToken = txn_token

    def get_txn_token(self):
        return self.txnToken

    def set_is_promo_code_valid(self, is_promo_code_valid):
        self.isPromoCodeValid = is_promo_code_valid

    def get_is_promo_code_valid(self):
        return self.isPromoCodeValid

    def set_is_authenticated(self, is_authenticated):
        self.authenticated = is_authenticated

    def get_is_authenticated(self):
        return self.authenticated

    def set_callback_url(self, callback_url):
        self.callbackUrl = callback_url

    def get_callback_url(self):
        return self.callbackUrl

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)
