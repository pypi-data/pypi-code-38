from pyvxclient.resource import Resource


class Order(Resource):

    _default_sort = ("id", "order_number")
