from pyvxclient.resource import Resource


class ObjectAddress(Resource):

    def get(self, object_number):
        return self.client.object.getObjectAddress(object_number=object_number).response().result
