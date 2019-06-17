from pyvxclient.resource import ResourceGeneric


class Service(ResourceGeneric):

    _default_sort = ("id", "order_number")
