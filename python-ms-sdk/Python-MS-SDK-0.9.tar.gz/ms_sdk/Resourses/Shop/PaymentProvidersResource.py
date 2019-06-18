from ms_sdk.Resourses import Resource


class PaymentProvidersResource(Resource):
    """
    Class PaymentProvidersResource
    :method PaymentProvider get(int id):
    :method PaymentProvider first():
    :method PaymentProvider[] all():
    :method PaymentProvider update(id, data):
    :method PaymentProvider create(data):
    """

    def getURI(self):
        return 'paymentproviders'