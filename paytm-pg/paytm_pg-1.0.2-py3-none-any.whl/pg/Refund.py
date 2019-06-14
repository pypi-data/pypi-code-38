from sys import exc_info

from paytmpg.pg.constants.MerchantProperty import MerchantProperty

from paytmpg.pg.utils.SignatureUtil import generateSignature
from paytmpg.pg.utils.CommonUtil import CommonUtil
from paytmpg.pg.utils.stringUtil import is_empty, format_string

from paytmpg.pg.request.RefundInitiateRequest import RefundInitiateRequest
from paytmpg.pg.response.AsyncRefundResponse import AsyncRefundResponse
from paytmpg.pg.response.NativeRefundStatusResponse import NativeRefundStatusResponse
from paytmpg.pg.request.NativeRefundStatusRequest import NativeRefundStatusRequest
from paytmpg.pg.Request import Request
from paytmpg.pg.SDKException import SDKException
from paytmpg.merchant.models.SDKResponse import SDKResponse


class Refund:
    """This class is handle all the Refund calls from DemoApp.py and create
    request objects and make call to the respective controller
    This class receive the Paytm response objects and translate the to their
    respective merchant response objects and returns call to DemoApp
    """
    @classmethod
    def doRefund(cls, refund_detail):
        """
        :param refund_detail: all parameter are in refund detail which is required to make request
        :return: SDKResponse object
        """
        MerchantProperty.set_logger_name(CommonUtil.get_unique_request_id())
        try:
            if not MerchantProperty.is_initialized:
                MerchantProperty.logger.debug("Refund :: do_refund :: MerchantProperties are not initialized.")
                return CommonUtil.get_sdk_response(SDKException.get_merchant_property_initialization_exception(),
                                                   AsyncRefundResponse())
            MerchantProperty.logger.info("Refund :: do_refund for refund_detail: {}".format(refund_detail))
            cls.__validate_refund(refund_detail)
            request = cls.__create_refund_initiate_request(refund_detail)
            cls.__set_signature(request.get_head(), request.get_body())
            response = SDKResponse().set_response_object(AsyncRefundResponse())
            Request.process(request, MerchantProperty.get_refund_url(), response,
                            refund_detail.get_read_timeout())
            return response
        except Exception:
            return CommonUtil.get_sdk_response(exc_info()[1], AsyncRefundResponse())

    @staticmethod
    def __set_signature(head, body):
        """
        :param head: in which checksum attribute will be added
        :param body: value of checksum will be created over it's string value
        :return: None. As head is augmented by signature value
        """
        MerchantProperty.logger.debug("Refund:: set signature :: body is {}".format(format_string(body)))
        signature = generateSignature(format_string(body), MerchantProperty.get_merchant_key())
        head.set_signature(signature)

    @staticmethod
    def __create_refund_initiate_request(refund_detail):
        """
        :param refund_detail: has all parameter
        :return: RefundInitiateRequest object
        """
        head = CommonUtil.get_secure_request_header(MerchantProperty.get_client_id())
        body = refund_detail._RefundDetail__create_refund_initiate_request_body()
        return RefundInitiateRequest().set_head(head).set_body(body)

    @staticmethod
    def __validate_refund(refund_detail):
        """validate_refund checks if all mandatory parameters are present for Refund api
        If not, then is will throw the RequestValidationException exception
        :param refund_detail: RefundInitiateRequest object
        :return: raise exception if any mandatory parameter is missing
        """
        MerchantProperty.logger.info("Refund :: validate_refund for refund_detail : {}".format(refund_detail))
        if is_empty(refund_detail.get_order_id())\
                or is_empty(refund_detail.get_ref_id())\
                or is_empty(refund_detail.get_txn_id())\
                or is_empty(refund_detail.get_refund_amount()):
            raise SDKException.get_missing_mandatory_parameters_exception()

    @classmethod
    def getRefundStatus(cls, refund_status_detail):
        MerchantProperty.set_logger_name(CommonUtil.get_unique_request_id())
        try:
            if not MerchantProperty.is_initialized:
                MerchantProperty.logger.debug("Refund :: get_refund_status :: MerchantProperties are not initialized.")
                return CommonUtil.get_sdk_response(SDKException.get_merchant_property_initialization_exception(),
                                                   NativeRefundStatusResponse())
            MerchantProperty.logger.info("Refund :: get_refund_status : for refund status detail: {}".format(refund_status_detail))
            cls.__validate_refund_status(refund_status_detail)
            request = cls.__create_refund_status_request(refund_status_detail)
            cls.__set_signature(request.get_head(), request.get_body())
            response = SDKResponse().set_response_object(NativeRefundStatusResponse())
            Request.process(request, MerchantProperty.get_refund_status_url(), response, refund_status_detail.get_read_timeout())
            return response
        except Exception:
            return CommonUtil.get_sdk_response(exc_info()[1], NativeRefundStatusResponse())

    @staticmethod
    def __create_refund_status_request(refund_status_detail):
        """
        :param refund_status_detail:
        :return: NativeRefundStatusRequest object
        """
        head = CommonUtil.get_secure_request_header(MerchantProperty.get_client_id(), None)
        body = refund_status_detail._RefundStatusDetail__create_native_refund_status_request_body()
        return NativeRefundStatusRequest().set_head(head).set_body(body)

    @staticmethod
    def __validate_refund_status(refund_status_detail):
        MerchantProperty.logger.info("Refund :: validate refund status for refund_status_detail: {}".format(refund_status_detail))
        if is_empty(refund_status_detail.get_order_id())\
                or is_empty(refund_status_detail.get_ref_id()):
            MerchantProperty.logger.debug("validate refund status is false")
            raise SDKException.get_missing_mandatory_parameters_exception()
        MerchantProperty.logger.debug("validate refund_status true")

    def __dir__(self):
        return ""
