from services.resource import APIResource, Configuration

class PropellerService(APIResource):
    def __init__(self):
        config = Configuration("https://ssp-api.propellerads.com/v5", auth_handler=False, handler=None, service_name='Propellerads Service(AMP)')
        super().__init__(config)


    def get_adv_statistics(self):
        querystring = '/adv/statistics'
        return self.get(querystring)


# import httpretty
# @httpretty.activate
# def a():
#     httpretty.register_uri(httpretty.GET, "https://ssp-api.propellerads.com/v5/adv/statistics", body="this is a test")
#     res = PropellerService().get_adv_statistics()
#     print(res.text)
# a()