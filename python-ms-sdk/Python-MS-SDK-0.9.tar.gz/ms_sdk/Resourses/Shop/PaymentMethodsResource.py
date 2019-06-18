from ms_sdk.Resourses import Resource


class PaymentMethodsResource(Resource):
    """
    Class PaymentMethodsResource
    :method PaymentMethod get(int id):
    :method PaymentMethod first():
    :method PaymentMethod[] all():
    :method PaymentMethod update(id, data):
    :method PaymentMethod create(data):
    """

    def getURI(self):
        return 'paymentmethods'