from ms_sdk.Resourses import Resource


class AddressResource(Resource):
    """
    Class AddresssResource
    :method Address get(int id):
    :method Address first():
    :method Address[] all():
    :method Address update(id, data):
    :method Address create(data):
    """

    def getURI(self):
        return 'addresses'