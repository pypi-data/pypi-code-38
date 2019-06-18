from ms_sdk.Resourses.Resource import Resource


class BrandsResource(Resource):
    """
    Class BrandsResource
    :method Brand get(int id):
    :method Brand first():
    :method Brand[] all():
    :method Brand update(id, data):
    :method Brand create(data):
    """

    def getURI(self):
        return 'brands'
