from sys import exc_info

from paytmpg.pg.request.InitiateTransactionRequest import InitiateTransactionRequest
from paytmpg.pg.request.NativePaymentStatusRequest import NativePaymentStatusRequest

from paytmpg.pg.response.InitiateTransactionResponse import InitiateTransactionResponse
from paytmpg.pg.response.NativePaymentStatusResponse import NativePaymentStatusResponse

from paytmpg.pg.utils.CommonUtil import CommonUtil
from paytmpg.pg.utils.SignatureUtil import generateSignature
from paytmpg.pg.utils.stringUtil import is_empty, format_string

from paytmpg.pg.constants.MerchantProperty import MerchantProperty

from paytmpg.pg.SDKException import SDKException
from paytmpg.pg.Request import Request
from paytmpg.merchant.models.SDKResponse import SDKResponse


class Payment:
    """This class handle all call(which is from DemoApp) related to create transaction and payment status  
    """
    @classmethod
    def createTxnToken(cls, payment_details):
        """
        :param payment_details: has all mandatory parameter and some others
        :return: SDKResponse {jsonData, InitiateTransactionResponse}
        """
        MerchantProperty.set_logger_name(CommonUtil.get_unique_request_id())
        try:
            if not MerchantProperty.is_initialized:
                return CommonUtil.get_sdk_response(SDKException.get_merchant_property_initialization_exception(), InitiateTransactionResponse())
            MerchantProperty.logger.info("Payment :: create_txn_token payment_details: {}".format(payment_details))
            cls.__validate_create_txn_token(payment_details)
            request = cls.__create_initiate_transaction_request(payment_details)
            cls.__set_signature(request.get_head(), request.get_body())
            response = SDKResponse().set_response_object(InitiateTransactionResponse())
            url = MerchantProperty.get_initiate_txn_url() + '?' + "mid=" + request.get_body().get_mid() + \
                "&orderId=" + request.get_body().get_order_id()
            Request.process(request, url, response, payment_details.get_read_timeout())
            return response
        except Exception:
            return CommonUtil.get_sdk_response(exc_info()[1], InitiateTransactionResponse())

    @staticmethod
    def __create_initiate_transaction_request(payment_details):
        """This method convert payment_details into InitiateTransactionRequestBody()
        :param payment_details: has all mandatory parameter and some others
        :return: InitiateTransactionRequest object
        """
        head = CommonUtil.get_secure_request_header(MerchantProperty.get_client_id(), payment_details.get_channel_id())
        body = payment_details._PaymentDetail__create_initiate_transaction_request_body()
        return InitiateTransactionRequest().set_head(head).set_body(body)

    @staticmethod
    def __set_signature(head, body):
        """
        :param head: secure-header
        :param body: body of which we are making checksum and adding to head
        :return:
        """
        signature = generateSignature(format_string(body), MerchantProperty.get_merchant_key())
        head.set_signature(signature)

    @staticmethod
    def __validate_create_txn_token(payment_details):
        """Checking mandatory field it has or not
        :param payment_details:
        :return: if mandatory parameter is not there return SDKException
        """
        MerchantProperty.logger.info("Payment :: validateCreateTxnToken for payment_details: {0} ".format(payment_details))
        if is_empty(payment_details.get_order_id()) or not payment_details.get_txn_amount()\
                or is_empty(payment_details.get_txn_amount().get_value()) or not payment_details.get_user_info()\
                or is_empty(payment_details.get_user_info().get_cust_id()):
            raise SDKException.get_missing_mandatory_parameters_exception()

    @staticmethod
    def __create_native_payment_status_request(payment_status_detail):
        """
        :param payment_status_detail: has all mandatory parameter and some others
        :return: NativePaymentStatusRequest object
        """
        head = CommonUtil.get_secure_request_header(MerchantProperty.get_client_id(), None)
        body = payment_status_detail._PaymentStatusDetail__create_native_payment_status_request_body()
        request = NativePaymentStatusRequest()
        request.set_head(head)
        request.set_body(body)
        return request

    @classmethod
    def getPaymentStatus(cls, payment_status_detail):
        """
        :param payment_status_detail: it has all parameter to make request
        :return: SDKResponse { json response data, NativePaymentStatusRequest object}
        """
        MerchantProperty.set_logger_name(CommonUtil.get_unique_request_id())
        try:
            if not MerchantProperty.is_initialized:
                return CommonUtil.get_sdk_response(SDKException.get_merchant_property_initialization_exception(),
                                                   NativePaymentStatusRequest())
            MerchantProperty.logger.info(
                "Payment :: get_payment_status payment_status_detail: {}".format(payment_status_detail))
            cls.__validate_get_payment_status(payment_status_detail)
            request = cls.__create_native_payment_status_request(payment_status_detail)
            cls.__set_signature(request.get_head(), request.get_body())
            response = SDKResponse().set_response_object(NativePaymentStatusResponse())
            Request.process(request, MerchantProperty.get_payment_status_url(), response
                            , payment_status_detail.get_read_timeout())
            return response
        except Exception:
            return CommonUtil.get_sdk_response(exc_info()[1], NativePaymentStatusResponse())

    @staticmethod
    def __validate_get_payment_status(payment_status_detail):
        """
        :param payment_status_detail:
        :return: will raise exception if there is missing of any mandatory parameter
        """
        MerchantProperty.logger.info(
            "Payment :: validate_get_payment_status for payment_status_detail: {}".format(payment_status_detail))
        if is_empty(payment_status_detail.get_order_id()):
            raise SDKException.get_missing_mandatory_parameters_exception()

    def __dir__(self):
        return ""
