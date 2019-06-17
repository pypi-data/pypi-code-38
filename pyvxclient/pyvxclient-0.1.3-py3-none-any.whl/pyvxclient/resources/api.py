from pyvxclient.resource import Resource


class Api(Resource):

    def get(self):
        return self.client.api.getApi().response().result
