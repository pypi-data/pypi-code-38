import base64
import os
from pathlib import Path
from .kairos import KairosConnector

class ProficloudMetrics(KairosConnector):
    """
    Initialize TSD Metrics class.

    :type token: str
    :param token: base64 encoded login token (can also be the name of a file containing the token)
    :type trustEnvironment: boolean
    :param trustEnvironment: Load proxy information from environment (default=False)
    :type useStaging: boolean
    :param useStaging: Use staging environment instead of production (default=False)
    :type disableSSLVerification: boolean
    :param disableSSLVerification: Disable SSL Verification. Useful when behind SSL proxy. Only disable verification if there is no other option!
    :type proxies: dict
    :param proxies: Proxy information. Default: None. Example value: {"http": "http://127.0.0.1:3128", "https": "http://127.0.0.1:3128"} This will force trustEnvironment to False.
    """

    def __init__(self, token, trustEnvironment=False, useStaging=False, disableSSLVerification=False, proxies=None):
        super().__init__(url="", headers=None, trustEnvironment=trustEnvironment, disableSSLVerification=disableSSLVerification, tags=None, proxies=proxies)

        self.url = "https://tsd.proficloud.net/ds/v1/kairos/"
        """The base url for the REST access. This is the base url of the KairosDB API. Default is the url for proficloud.net TSD service."""
        if useStaging:
            self.url = "https://tsd.proficloud-staging.net/ds/v1/kairos/"

        if os.path.isfile(token):
            token = Path(token).read_text()

        self.headers = { "Content-Type" : "application/json", "Authorization" : "Basic "+token }
        """The headers for the REST communication"""
    
    @staticmethod
    def generateToken(name, password):
        """
        Generate a logintoken for Proficloud for a given username and password.

        :type name: str
        :param name: the account id
        :type password: str
        :param password: the api credentials password
        :rtype: str
        :return: Base64 encoded logintoken
        """
        cred = name + ":" + password
        return base64.b64encode(cred.encode()).decode('utf-8')

    def add(self, payload):
        """
        This is not yet supported by TSD.
        """
        raise Exception("Adding Metrics is not yet supported by TSD.")

    def addMetrics(self, metricnames, metricvalues, timestamp=None):
        """
        This is not yet supported by TSD.
        """
        raise Exception("Adding Metrics is not yet supported by TSD.")

    def addMetricsBatch(self, dataframe, timestampColumnName="Timestamp"):
        """
        This is not yet supported by TSD.
        """
        raise Exception("Adding Metrics is not yet supported by TSD.")

