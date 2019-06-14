try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from sys import version_info
from os.path import abspath


class LibraryConstants:
    """ Below constants are used in API calling
    """
    VERSION = "v2"
    DATE_FORMAT = "yyyy.MM.dd.HH.mm.ss z"
    STAGING_ENVIRONMENT = "STAGE"
    PRODUCTION_ENVIRONMENT = "PROD"

    """Status message can be returned in case of Api Success"""
    SUCCESS_STATUS = "S"
    PENDING_STATUS = "PENDING"
    TXN_SUCCESS_STATUS = "TXN_SUCCESS"
    """Test String used in API callings"""
    TRUE_TEXT = 'true'
    FALSE_TEXT = 'false'
    MID_TEXT = 'mid'
    ORDER_ID_TEXT = 'orderId'
    CONTENT_TYPE_TEXT = 'Content-Type'
    APPLICATION_JSON_TEXT = 'application/json'
    UTF_8_TEXT = 'UTF-8'
    SUCCESS_TEXT = 'SUCCESS'
    HEAD_TEXT = 'head'
    BODY_TEXT = 'body'
    SIGNATURE_TEXT = 'signature'
    PYTHON_SDK_TEXT = "PYTHON-SDK"
    X_REQUEST_ID = "X-Request-ID"
    """below text as these are used input name for redirection
    flow in process transaction api calling"""
    MID_TEXT_DEFAULT = 'MID'
    WEBSITE_TEXT_DEFAULT = 'WEBSITE'
    CALLBACK_URL_TEXT_DEFAULT = 'CALLBACK_URL'
    CHECKSUM_HASH_TEXT_DEFAULT = 'CHECKSUMHASH'

    # this jsp is used in redirection flow
    DEFAULT_REDIRECT_JSP = "pgRedirect.jsp"
    REQUEST_TYPE_PAYMENT = "Payment"
    MEDIA_TYPE_JSON = "application/json; charset=utf-8"

    config = configparser.ConfigParser()
    file_path = '/'.join(abspath(__file__).split('/')[:-4])
    file_abs_path = file_path + "/VERSION.ini"
    config.read(file_abs_path)
    if version_info[0] < 3:
        PYTHON_SDK_VERSION = config.get('VERSION_INFO', 'package_version')
    else:
        PYTHON_SDK_VERSION = config['VERSION_INFO']['package_version']

    class Request:
        FOOD_WALLET = "FOOD"
        GIFT_WALLET = "GIFT"
