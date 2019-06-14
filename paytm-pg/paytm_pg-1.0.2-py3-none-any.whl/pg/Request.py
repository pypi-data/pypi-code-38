from requests import post

from paytmpg.pg.constants.MerchantProperty import MerchantProperty
from paytmpg.pg.constants.LibraryConstants import LibraryConstants

from paytmpg.pg.utils.ConverterUtil import JsonToObject
from paytmpg.pg.utils.SignatureUtil import verifySignature
from paytmpg.pg.SDKException import SDKException
from paytmpg.pg.utils.stringUtil import is_empty, format_string


class Request:

    headers = {'Content-type': LibraryConstants.APPLICATION_JSON_TEXT}

    @classmethod
    def process(cls, request, url, response, read_timeout=30):
        """
        :param request: it contain head and body which we want to transmit over network
        :param url: on which we want to make hit
        :param response: object in which value of response will be putted
        :param read_timeout: this is in "Second" unit
        :return: None, it is just setting value in response object
        """
        cls.headers[LibraryConstants.X_REQUEST_ID] = MerchantProperty.request_id
        post_args = {
            'headers': cls.headers,
            'timeout': (MerchantProperty.connect_timeout, read_timeout),
            'data': format_string(request)
        }
        res = post(url, **post_args)
        MerchantProperty.logger.info("Request :: do_transaction for request: {} ".format(format_string(request)))
        MerchantProperty.logger.info("Request :: do_transaction response for request: {} ".format(res))
        MerchantProperty.logger.info("Request :: do_transaction response content for request: {} ".format(res.content))
        response.set_json_response(res.content)
        if res.status_code == "500" or res.status_code == "400":
            MerchantProperty.logger.info(
                "Request :: do_transaction for request: status code {}".format(res.status_code))
            return SDKException.get_sdk_exception(str(res.content))
        str_body = cls.__get_body_from_response_content(str(res.content))
        request_response = res.json()
        JsonToObject(request_response, response.get_response_object())
        result_info = response.get_response_object().get_body().get_result_info()
        if response.get_response_object().get_head().get_signature() is not None and (
                LibraryConstants.SUCCESS_STATUS == result_info.get_result_status()
                or LibraryConstants.TXN_SUCCESS_STATUS == result_info.get_result_status()
                or LibraryConstants.PENDING_STATUS == result_info.get_result_status()) and \
                not verifySignature(str_body, MerchantProperty.get_merchant_key(),
                                    response.get_response_object().get_head().get_signature()):
            raise SDKException.get_signature_validation_failed_exception(res.content)

    @staticmethod
    def __get_body_from_response_content(content):
        if is_empty(content) or ('"body":{' not in content) or ('"head":{' not in content):
            raise SDKException.get_sdk_exception("Received response body is not proper.")
        MerchantProperty.logger.debug("Request :: get_body_from_response_content content: {}".format(content))
        head_idx = content.find(LibraryConstants.HEAD_TEXT, 0, len(content))
        start_idx, end_idx = content.find(LibraryConstants.BODY_TEXT, 0, len(content)) + 6, len(
            content) - (2 if content.endswith('\'') else 1)
        if head_idx > start_idx:
            end_idx = head_idx-2
        MerchantProperty.logger.debug(
            "Request :: get_body_from_response_content body: {}".format(content[start_idx:end_idx]))
        return content[start_idx:end_idx]
