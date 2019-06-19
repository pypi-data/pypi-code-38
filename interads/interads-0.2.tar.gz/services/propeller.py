from core.delegation.responsehandler import ResponseHandler
from core.resource import APIResource, Configuration
from services.responses import PropellerObject

class PropellerService(APIResource):
    def __init__(self):
        config = Configuration("https://ssp-api.propellerads.com/v5", auth_handler=False, handler=PropellerHandler, service_name='Propellerads Service(AMP)')
        super().__init__(config)


    def get_adv_statistics(self):
        querystring = '/adv/statistics'
        return self.get(querystring)


class PropellerHandler(ResponseHandler):
    @staticmethod
    def handle(result):
        res = result.json()
        return PropellerObject(res)


