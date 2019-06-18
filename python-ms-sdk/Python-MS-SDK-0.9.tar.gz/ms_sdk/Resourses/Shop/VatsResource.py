from ms_sdk.Resourses import Resource


class VatsResource(Resource):
    """
    Class VatsResource
    :method Vat get(int id):
    :method Vat first():
    :method Vat[] all():
    :method Vat update(id, data):
    :method Vat create(data):
    """

    def getURI(self):
        return 'vat'