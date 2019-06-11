from paytmpg.pg.utils.stringUtil import make_string, equals


class InitiateTransactionRequestBody:

    def __init__(self):
        self.requestType = None
        self.mid = None
        self.orderId = None
        self.websiteName = None
        self.txnAmount = None
        self.userInfo = None
        self.paytmSsoToken = None
        self.enablePaymentMode = None
        self.disablePaymentMode = None
        self.promoCode = None
        self.callbackUrl = None
        self.goods = None
        self.shippingInfo = None
        self.extendInfo = None
        self.emiOption = None
        self.cardTokenRequired = None
        self.cartValidationRequired = None

    def set_request_type(self, request_type):
        self.requestType = request_type

    def get_request_type(self):
        return self.requestType

    def set_mid(self, mid):
        self.mid = mid

    def get_mid(self):
        return self.mid

    def set_order_id(self, order_id):
        self.orderId = order_id

    def get_order_id(self):
        return self.orderId

    def set_website_name(self, website_name):
        self.websiteName = website_name

    def get_website_name(self):
        return self.websiteName

    def set_txn_amount(self, txn_amount):
        self.txnAmount = txn_amount

    def get_txn_amount(self):
        return self.txnAmount

    def set_user_info(self, user_info):
        self.userInfo = user_info

    def get_user_info(self):
        return self.userInfo

    def set_paytm_sso_token(self, paytm_sso_token):
        self.paytmSsoToken = paytm_sso_token

    def get_paytm_sso_token(self):
        return self.paytmSsoToken

    def set_enable_payment_mode(self, enable_payment_mode):
        self.enablePaymentMode = enable_payment_mode

    def get_enable_payment_mode(self):
        return self.enablePaymentMode

    def set_disable_payment_mode(self, disable_payment_mode):
        self.disablePaymentMode = disable_payment_mode

    def get_disable_payment_mode(self):
        return self.disablePaymentMode

    def set_promo_code(self, promo_code):
        self.promoCode = promo_code

    def get_promo_code(self):
        return self.promoCode

    def set_callback_url(self, callback_url):
        self.callbackUrl = callback_url

    def get_callback_url(self):
        return self.callbackUrl

    def set_goods(self, goods):
        self.goods = goods

    def get_goods(self):
        return self.goods

    def set_shipping_info(self, shipping_info):
        self.shippingInfo = shipping_info

    def get_shipping_info(self):
        return self.shippingInfo

    def set_extend_info(self, extend_info):
        self.extendInfo = extend_info

    def get_extend_info(self):
        return self.extendInfo

    def set_emi_option(self, emi_option):
        self.emiOption = emi_option

    def get_emi_option(self):
        return self.emiOption

    def set_card_token_required(self, card_token_required):
        self.cardTokenRequired = card_token_required

    def get_card_token_required(self):
        return self.cardTokenRequired

    def set_cart_validation_required(self, cart_validation_required):
        self.cartValidationRequired = cart_validation_required

    def get_cart_validation_required(self):
        return self.cartValidationRequired

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)
