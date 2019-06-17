from pyvxclient.resource import ResourceGeneric


class Order(ResourceGeneric):

    _default_sort = ("id", "order_number")
