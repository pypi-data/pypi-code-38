from paytmpg.pg.constants.MerchantProperty import MerchantProperty
from paytmpg.pg.constants.LibraryConstants import LibraryConstants
from paytmpg.pg.request.InitiateTransactionRequestBody import InitiateTransactionRequestBody
from paytmpg.pg.utils.stringUtil import make_string, equals


class PaymentDetail:

    def __init__(self, payment_detail_builder):
        self.__channelId = payment_detail_builder.channelId
        self.__orderId = payment_detail_builder.orderId
        self.__txnAmount = payment_detail_builder.txnAmount
        self.__userInfo = payment_detail_builder.userInfo
        self.__paytmSsoToken = payment_detail_builder.paytmSsoToken
        self.__enablePaymentMode = payment_detail_builder.enablePaymentMode
        self.__disablePaymentMode = payment_detail_builder.disablePaymentMode
        self.__goods = payment_detail_builder.goods
        self.__shippingInfo = payment_detail_builder.shippingInfo
        self.__extendInfo = payment_detail_builder.extendInfo
        self.__promoCode = payment_detail_builder.promoCode
        self.__emiOption = payment_detail_builder.emiOption
        self.__cardTokenRequired = payment_detail_builder.cardTokenRequired
        self.__readTimeout = payment_detail_builder.readTimeout

    def get_channel_id(self):
        return self.__channelId

    def get_order_id(self):
        return self.__orderId

    def get_txn_amount(self):
        return self.__txnAmount

    def get_user_info(self):
        return self.__userInfo

    def get_paytm_sso_token(self):
        return self.__paytmSsoToken

    def get_enable_payment_mode(self):
        return self.__enablePaymentMode

    def get_disable_payment_mode(self):
        return self.__disablePaymentMode

    def get_goods(self):
        return self.__goods

    def get_shipping_info(self):
        return self.__shippingInfo

    def get_promo_code(self):
        return self.__promoCode

    def get_extend_info(self):
        return self.__extendInfo

    def get_emi_option(self):
        return self.__emiOption

    def get_card_token_required(self):
        return self.__cardTokenRequired

    def get_read_timeout(self):
        return self.__readTimeout

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)

    def __dir__(self):
        return ""

    def __create_initiate_transaction_request_body(self):
        body = InitiateTransactionRequestBody()

        body.set_request_type(LibraryConstants.REQUEST_TYPE_PAYMENT)
        body.set_mid(MerchantProperty.get_mid())
        body.set_website_name(MerchantProperty.get_website())
        body.set_callback_url(MerchantProperty.get_callback_url())

        body.set_order_id(self.get_order_id())
        body.set_txn_amount(self.get_txn_amount())
        body.set_user_info(self.get_user_info())
        body.set_paytm_sso_token(self.get_paytm_sso_token())
        body.set_enable_payment_mode(self.get_enable_payment_mode())
        body.set_disable_payment_mode(self.get_disable_payment_mode())
        body.set_promo_code(self.get_promo_code())
        body.set_goods(self.get_goods())
        body.set_shipping_info(self.get_shipping_info())
        body.set_extend_info(self.get_extend_info())
        body.set_emi_option(self.get_emi_option())
        body.set_card_token_required(self.get_card_token_required())
        return body


class PaymentDetailsBuilder:

    channelId = None
    orderId = None
    txnAmount = None
    userInfo = None
    paytmSsoToken = None
    enablePaymentMode = None
    disablePaymentMode = None
    goods = None
    shippingInfo = None
    promoCode = None
    extendInfo = None
    emiOption = None
    cardTokenRequired = None
    readTimeout = None

    def __init__(self, channel_id, order_id, txn_amount, user_info):
        self.channelId = channel_id
        self.orderId = order_id
        self.txnAmount = txn_amount
        self.userInfo = user_info
        self.readTimeout = 30

    def build(self):
        return PaymentDetail(self)

    def set_channel_id(self, channel_id):
        self.channelId = channel_id
        return self

    def set_order_id(self, order_id):
        self.orderId = order_id
        return self

    def set_txn_amount(self, txn_amount):
        self.txnAmount = txn_amount
        return self

    def set_user_info(self, user_info):
        self.userInfo = user_info
        return self

    def set_paytm_sso_token(self, paytm_sso_token):
        self.paytmSsoToken = paytm_sso_token
        return self

    def set_enable_payment_mode(self, enable_payment_mode):
        self.enablePaymentMode = enable_payment_mode
        return self

    def set_disable_payment_mode(self, disable_payment_mode):
        self.disablePaymentMode = disable_payment_mode
        return self

    def set_goods(self, goods):
        self.goods = goods
        return self

    def set_shipping_info(self, shipping_info):
        self.shippingInfo = shipping_info
        return self

    def set_promo_code(self, promo_code):
        self.promoCode = promo_code
        return self

    def set_extend_info(self, extend_info):
        self.extendInfo = extend_info
        return self

    def set_emi_option(self, emi_option):
        self.emiOption = emi_option
        return self

    def set_card_token_required(self, card_token_required):
        self.cardTokenRequired = card_token_required
        return self

    def set_read_timeout(self, read_timeout):
        self.readTimeout = read_timeout
        return self

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError(" Can not be set ".format(key))
        self.__dict__[key] = value
