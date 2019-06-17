from pyvxclient.resource import Resource


class ObjectInfo(Resource):

    def get(self, object_number):
        return self.client.object.getObjectInfo(number=object_number).response().result
