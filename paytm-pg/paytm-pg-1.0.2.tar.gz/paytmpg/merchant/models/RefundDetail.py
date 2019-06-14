from paytmpg.pg.constants.MerchantProperty import MerchantProperty
from paytmpg.pg.request.RefundInitiateRequestBody import RefundInitiateRequestBody
from paytmpg.pg.utils.stringUtil import make_string, equals


class RefundDetail:

    def __init__(self, refund_detail_builder):
        self.__orderId = refund_detail_builder.order_id
        self.__refId = refund_detail_builder.ref_id
        self.__txnId = refund_detail_builder.txn_id
        self.__refundAmount = refund_detail_builder.refund_amount
        self.__comments = refund_detail_builder.comments
        # [dict of user_sub_wallet_type: big_decimal]
        self.__subwalletAmount = refund_detail_builder.sub_wallet_amount
        # [dict of str:object]
        self.__extraParamsMap = refund_detail_builder.extra_params_map
        self.__readTimeout = refund_detail_builder.read_timeout

    def get_order_id(self):
        return self.__orderId

    def get_ref_id(self):
        return self.__refId

    def get_txn_id(self):
        return self.__txnId

    def get_refund_amount(self):
        return self.__refundAmount

    def get_comments(self):
        return self.__comments

    def get_sub_wallet_amount(self):
        return self.__subwalletAmount

    def get_extra_params_map(self):
        return self.__extraParamsMap

    def get_read_timeout(self):
        return self.__readTimeout

    def __str__(self):
        return ""

    def __eq__(self, other):
        return equals(self)

    def __dir__(self):
        return ""

    def __create_refund_initiate_request_body(self):
        refund_initiate_request_body = RefundInitiateRequestBody()
        refund_initiate_request_body.set_mid(MerchantProperty.get_mid())
        refund_initiate_request_body.set_order_id(self.get_order_id())
        refund_initiate_request_body.set_ref_id(self.get_ref_id())
        refund_initiate_request_body.set_extra_parameter_map(self.get_extra_params_map())
        refund_initiate_request_body.set_txn_id(self.get_txn_id())
        refund_initiate_request_body.set_refund_amount(self.get_refund_amount())
        refund_initiate_request_body.set_comments(self.get_comments())
        refund_initiate_request_body.set_sub_wallet_amount(self.get_sub_wallet_amount())
        return refund_initiate_request_body


class RefundDetailBuilder:
    order_id = None
    ref_id = None
    txn_id = None
    refund_amount = None
    comments = None
    # [dict of user_sub_wallet_type: big_decimal]
    sub_wallet_amount = None
    # [dict of str:object]
    extra_params_map = None
    read_timeout = 30

    def __init__(self, order_id, ref_id, txn_id, refund_amount):
        self.order_id = order_id
        self.ref_id = ref_id
        self.txn_id = txn_id
        self.refund_amount = refund_amount

    def build(self):
        return RefundDetail(self)

    def set_order_id(self, order_id):
        self.order_id = order_id
        return self

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id
        return self

    def set_extra_params_map(self, extra_params_map):
        self.extra_params_map = extra_params_map
        return self

    def set_txn_id(self, txn_id):
        self.txn_id = txn_id
        return self

    def set_refund_amount(self, refund_amount):
        self.refund_amount = refund_amount
        return self

    def set_comments(self, comments):
        self.comments = comments
        return self

    def set_sub_wallet_amount(self, sub_wallet_amount):
        self.sub_wallet_amount = sub_wallet_amount
        return self

    def set_read_timeout(self, read_timeout):
        self.read_timeout = read_timeout
        return self

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self)

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError(" Can not be set ".format(key))
        self.__dict__[key] = value

    def __dir__(self):
        return ""
