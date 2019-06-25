import base64
import os
from pathlib import Path
from .kairos import KairosConnector
import pandas

class ProficloudMetrics(KairosConnector):
    """
    Initialize EWIMA Metrics class.

    :type clientToken: str
    :param clientToken: base64 encoded login token (can also be the name of a file containing the token)
    :type trustEnvironment: boolean
    :param trustEnvironment: Load proxy information from environment (default=False)
    :type useStaging: boolean
    :param useStaging: Use staging environment instead of production (default=False)
    :type disableSSLVerification: boolean
    :param disableSSLVerification: Disable SSL Verification. Useful when behind SSL proxy. Only disable verification if there is no other option!
    :type proxies: dict
    :param proxies: Proxy information. Default: None. Example value: {"http": "http://127.0.0.1:3128", "https": "http://127.0.0.1:3128"} This will force trustEnvironment to False.
    """

    def __init__(self, clientToken, trustEnvironment=False, useStaging=False, disableSSLVerification=False, proxies=None):
        super().__init__(url="", headers=None, trustEnvironment=trustEnvironment, disableSSLVerification=disableSSLVerification, tags=None, proxies=proxies)

        self.url = "https://emalytics.proficloud.net/ds/v1/kairos/"
        """The base url for the REST access. This is the base url of the KairosDB API. Default is the url for proficloud.net TSD service."""
        if useStaging:
            self.url = "https://ewima.proficloud-staging.net/ds/v1/kairos/"

        if os.path.isfile(clientToken):
            clientToken = Path(clientToken).read_text()

        self.headers = { 
            "Content-Type" : "application/json", 
            "Authorization" : "Basic "+clientToken
            }

        #Get the UUID, it is important for writes!
        cred = base64.b64decode(clientToken.encode()).decode('utf-8').split(":")
        self.tags = { "uuid" : cred[0] }

    
    @staticmethod
    def generateToken(uuid, password):
        """
        Generate a logintoken for Proficloud for a given username and password.

        :type uuid: str
        :param uuid: the account id
        :type password: str
        :param password: the api credentials password
        :rtype: str
        :return: Base64 encoded logintoken
        """
        cred = uuid + ":" + password
        return base64.b64encode(cred.encode()).decode('utf-8')

    @staticmethod
    def generateMetricsCsv(metrics, filename):
        """
        Generate csv file for importing into client metrics. 
        Just provide a list with desired metric names.

        :type metrics: list of strings
        :param metrics: The list of metric names to generate
        :type filename: str
        :param filename: The target filename
        """
        df = pandas.DataFrame(data={"selector": metrics, "metricalias": metrics})
        df.to_csv(filename, sep=';',index=False)

