from ms_sdk.Resourses import Resource


class OrderItemsResource(Resource):
    """
    Class OrderItemsResource
    :method OrderItem get(int id):
    :method OrderItem first():
    :method OrderItem[] all():
    :method OrderItem update(id, data):
    :method OrderItem create(data):
    """

    def getURI(self):
        return 'orderitems'