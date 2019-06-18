from ms_sdk.Resourses import Resource


class DeliveryProvidersResource(Resource):
    """
    Class DeliveryProvidersResource
    :method DeliveryProvider get(int id):
    :method DeliveryProvider first():
    :method DeliveryProvider[] all():
    :method DeliveryProvider update(id, data):
    :method DeliveryProvider create(data):
    """

    def getURI(self):
        return 'deliveryproviders'