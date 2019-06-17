from pyvxclient.resource import Resource


class Place(Resource):

    def get(self):
        return self.client.customer.getPlace().response().result
