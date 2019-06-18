from ms_sdk.Resourses import Resource


class DeliveryPaymentsResource(Resource):
    """
    Class DeliveryPaymentsResource
    :method DeliveryPaymentRelation get(int id):
    :method DeliveryPaymentRelation first():
    :method DeliveryPaymentRelation[] all():
    :method DeliveryPaymentRelation update(id, data):
    :method DeliveryPaymentRelation create(data):
    """

    def getURI(self):
        return 'deliverypaymentrelations'