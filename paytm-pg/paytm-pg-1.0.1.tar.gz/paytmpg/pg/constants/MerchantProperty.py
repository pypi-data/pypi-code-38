import logging

from paytmpg.pg.constants.LibraryConstants import LibraryConstants


class MerchantProperty:
    """This class is used to store all the merchant related constants that are
     common to all payments and orders
    """
    """This is true if merchant initialized the required parameter
    which is set by calling initialize method of this class.
    """
    is_initialized = False

    environment = LibraryConstants.STAGING_ENVIRONMENT

    """timeout constants in seconds default"""
    connect_timeout = 30
    read_timeout = 80

    """providing key and merchant id"""
    mid = None
    """WEBSITE should be webstaging for testing purpose
    for production it's value defined in documents"""
    website = "WEBSTAGING"
    merchant_key = ""

    client_id = ""

    """callback url on which paytmpg will respond for api calls"""
    callback_url = "https://pg-staging.paytm.in/MerchantSite/bankResponse"

    base_url = "https://securegw-stage.paytm.in"
    initiate_txn_url = base_url + "/theia/api/v1/initiateTransaction"
    refund_url = base_url + "/refund/api/v1/async/refund"
    payment_status_url = base_url + "/merchant-status/api/v1/getPaymentStatus"
    refund_status_url = "https://pgp-ite.paytm.in/refund/api/v1/refundStatus"

    """Logging instance 
    Used for logging information according to set level which can be changed while initializing parameter of merchant
    """
    logger = logging.getLogger("Paytm")
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s: %(levelname)s: %(message)s")
    log_handler.setFormatter(formatter)
    logger_disable = True
    logging_level = logging.DEBUG
    request_id = ""

    @classmethod
    def set_logger_name(cls, request_id):
        cls.logger.name = "Paytm " + request_id
        cls.request_id = request_id

    @classmethod
    def get_mid(cls):
        return cls.mid

    @classmethod
    def set_mid(cls, mid):
        cls.mid = mid

    @classmethod
    def get_website(cls):
        return cls.website

    @classmethod
    def set_website(cls, website):
        cls.website = website

    @classmethod
    def get_environment(cls):
        return cls.environment

    @classmethod
    def set_log_handler(cls, handler):
        if type(handler) is type(logging.StreamHandler()) or str(type(handler)) == str("<class 'logging.FileHandler'>"):
            cls.log_handler = handler

    @classmethod
    def set_logging_disable(cls, logger_disable):
        if type(logger_disable) is bool:
            cls.logger_disable = logger_disable

    @classmethod
    def set_logging_level(cls, logging_level):
        if type(logging_level) is type(cls.logging_level):
            cls.logging_level = logging_level

    @classmethod
    def initialize(cls, environment, mid, merchant_key, client_id, website):
        """
        :param environment:
        :param mid:
        :param merchant_key:
        :param client_id:
        :param website:
        :param callback_url:
        :return:
        """
        cls.is_initialized = True

        """initiate logger"""
        cls.logger.setLevel(cls.logging_level)
        cls.logger.addHandler(cls.log_handler)
        cls.logger.disabled = cls.logger_disable

        cls.set_environment(environment)
        cls.set_mid(mid)
        cls.set_merchant_key(merchant_key)
        cls.set_client_id(client_id)
        cls.set_website(website)

    @classmethod
    def set_merchant_key(cls, merchant_key):
        cls.merchant_key = merchant_key

    @classmethod
    def set_base_url(cls, base_url):
        cls.base_url = base_url

    @classmethod
    def get_base_url(cls):
        return cls.base_url

    @classmethod
    def get_connect_timeout(cls):
        return cls.connect_timeout

    @classmethod
    def set_connect_timeout(cls, connect_timeout):
        cls.connect_timeout = connect_timeout

    @classmethod
    def set_read_timeout(cls, read_timeout):
        cls.read_timeout = read_timeout

    @classmethod
    def get_read_timeout(cls):
        return cls.read_timeout

    @classmethod
    def set_timeout(cls, connect_timeout, read_timeout):
        cls.connect_timeout = connect_timeout
        cls.read_timeout = read_timeout

    @classmethod
    def set_environment(cls, environment):
        cls.environment = environment
        if cls.environment == LibraryConstants.PRODUCTION_ENVIRONMENT:
            cls.base_url = "https://securegw.paytm.in"
            cls.initiate_txn_url = cls.base_url + "/theia/api/v1/initiateTransaction"
            cls.refund_url = cls.base_url + "/refund/api/v2/async/refund"
            cls.payment_status_url = cls.base_url + "/merchant-status/api/v1/getPaymentStatus"

    @classmethod
    def set_client_id(cls, client_id):
        cls.client_id = client_id

    @classmethod
    def get_client_id(cls):
        return cls.client_id

    @classmethod
    def get_merchant_key(cls):
        return cls.merchant_key

    @classmethod
    def get_callback_url(cls):
        return cls.callback_url

    @classmethod
    def set_callback_url(cls, callback_url):
        cls.callback_url = callback_url

    @classmethod
    def get_callback_url_default(cls):
        return cls.callback_url_default

    @classmethod
    def set_callback_url_default(cls, callback_url_default):
        cls.callback_url_default = callback_url_default

    @classmethod
    def get_initiate_txn_url(cls):
        return cls.initiate_txn_url

    @classmethod
    def get_refund_url(cls):
        return cls.refund_url

    @classmethod
    def get_payment_status_url(cls):
        return cls.payment_status_url


    @classmethod
    def get_refund_status_url(cls):
        return cls.refund_status_url
