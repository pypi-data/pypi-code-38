from ms_sdk.Resourses import Resource


class OrderStatusesResource(Resource):
    """
    Class OrdersResource
    :method Order get(int id):
    :method Order first():
    :method Order[] all():
    :method Order update(id, data):
    :method Order create(data):
    """

    def getURI(self):
        return 'orderstatuses'