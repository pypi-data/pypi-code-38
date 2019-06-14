from paytmpg.pg.constants.MerchantProperty import MerchantProperty
from paytmpg.pg.request.NativeRefundStatusRequestBody import NativeRefundStatusRequestBody
from paytmpg.pg.utils.stringUtil import make_string, equals


class RefundStatusDetail:

    """Refund status Parameters"""
    def __init__(self, refund_status_detail_builder):
        """Unique order Id"""
        self.__order_id = refund_status_detail_builder.order_id
        """Unique ref id for each refund request"""
        self.__ref_id = refund_status_detail_builder.ref_id
        """Read TimeOut for Refund status Api """
        self.__read_timeout = refund_status_detail_builder.read_timeout

    def get_order_id(self):
        return self.__order_id

    def get_ref_id(self):
        return self.__ref_id

    def get_read_timeout(self):
        return self.__read_timeout

    def __str__(self):
        return ""

    def __eq__(self, other):
        return equals(self)

    def __dir__(self):
        return ""

    def __create_native_refund_status_request_body(self):
        return NativeRefundStatusRequestBody().set_mid(MerchantProperty.get_mid()).set_order_id(
            self.get_order_id()).set_ref_id(self.get_ref_id())


class RefundStatusDetailBuilder:
    """
    RefundStatusDetailBuilder is used to build the Refund Status object
    """
    order_id = None
    ref_id = None
    """in second """
    read_timeout = 5 * 60

    def __init__(self):
        pass

    def set_order_id(self, order_id):
        self.order_id = order_id
        return self

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id
        return self

    def set_read_timeout(self, read_timeout):
        self.read_timeout = read_timeout
        return self

    def build(self):
        return RefundStatusDetail(self)

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
