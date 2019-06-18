from ms_sdk.Exceptions.ConfigurationException import ConfigurationException
from ms_sdk.Lib.ServiceInjector import ServiceInjectorMixin


class Client(ServiceInjectorMixin):

    amountOfCalls = 0
    responseHistory = None
    version = 'v1'
    _async = False

    # Constructor
    def __init__(self, options: dict = {}):
        for (k, v) in options.items():
            setattr(self, k, v)

        if not (set(['gatewayUrl', 'clientId', 'secretKey']).issubset(
                set(options)) & all(options.values())):
            print('API connection data not set')
            raise ConfigurationException()

    # Getters methods
    def getGatewayUrl(self):
        return self.gatewayUrl

    def getClientId(self):
        return self.clientId

    def getSecretKey(self):
        return self.secretKey

    def getVersion(self):
        return self.version

    def getCallsStatistic(self):
        return {
            'amount': self.amountOfCalls,
            'history': self.responseHistory
        }

    def getAsync(self):
        return self._async

    # Setters methods
    def setAsync(self, _async):
        self._async = _async

    def setCallStatistic(self, callData):
        self.amountOfCalls += 1
        self.responseHistory = callData

    def setVersion(self, version):
        self.version = version
        return self

    def setSecretKey(self, secretKey):
        self.secretKey = secretKey
        return self

    def setClientId(self, clientId):
        self.clientId = clientId
        return self

    def setGateWayUrl(self, gatewayUrl):
        self.gatewayUrl = gatewayUrl
        return self
