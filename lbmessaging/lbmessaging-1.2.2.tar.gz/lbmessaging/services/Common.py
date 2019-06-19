from lbmessaging.exchanges.Common import get_connection, check_channel

ALL_EXCHANGES = {}
SERVICES_CHANNELS = {}


def MetaWrapper(exchange_class, exchange_map, service_name):
    """
    Method to dynamically instantiate an exchange and called its methods when
    a mapped method in the service is called. This Wrapper generates the
    associated execution code at runtime
    :param exchange_class: the name of the exchange class
    :param exchange_map: the name of the mapped method in the exchange
    :param service_name: the name of the service
    :return:
    """
    def function(*args, **kwargs):
        exchange = exchange_class(SERVICES_CHANNELS.get(service_name))
        try:
            obj_class = args[0].__class__.__name__
            if obj_class == service_name:
                args = args[1:]
        except:
            pass

        return getattr(exchange, exchange_map)(*args, **kwargs)
    return function


class ServiceMeta(type):
    """
    Meta class used by the BaseService in order to dynamically map the exchanges
    the the services at runtime. Multiple exchanges can be used in the same
    service.
    """
    def __new__(cls, name, bases, dct):
        """
        :param name: the name of the service
        :param bases: the base class of the service
        :param dct: the internal representation of the methods and arguments in
                    the service class
        :return:
        """
        if ALL_EXCHANGES.get(name, None):
            for exchange_data in ALL_EXCHANGES.get(name):
                exchange = exchange_data['exchange']
                service_map = exchange_data['mapping']
                if service_map:
                    for function in service_map.keys():
                        exchange_map = service_map[function]
                        dct[function] = MetaWrapper(exchange, exchange_map,
                                                    name)
        return type.__new__(cls, name, bases, dct)

"""
Parent of BaseService used as artifact to allow python 2 and python 3
compatibility and to prevent duplicated code
"""
try:
    exec('class BaseMetaService(metaclass=ServiceMeta): pass')
except SyntaxError:
    class BaseMetaService(object):
        __metaclass__ = ServiceMeta


class BaseService(BaseMetaService):
    """
    Base class for services that created the internal connection object to the
    message broker based on the init arguments
    """
    def __init__(self, host=None, username=None, passwd=None, port=5671,
                 vhost='/lhcb', use_ssl=True):
        """
        :param host: the RabbitMQ server hostname
        :param username: the RabbitMQ server username
        :param passwd: the RabbitMQ server password
        :param port: the RabbitMQ server port
        :param vhost: the RabbitMQ virtual host that should be used in the
                      connection
        :param use_ssl: if True, an encrypted connection is created, plain text
                        otherwise
        """
        connection = get_connection(host=host, username=username,
                                    passwd=passwd, port=port,
                                    vhost=vhost, use_ssl=use_ssl)
        self.channel = check_channel(None, connection=connection)
        SERVICES_CHANNELS[self.__class__.__name__] = self.channel


class ExposedIn():
    """
    Class used to decorate exchanges in order for the library to declare them
    dynamically in the services.
    """

    def __init__(self, service_name, mapping=None):
        """
        :param service_name: the name of the service in which the decorated
                             exchange should be declared
        :param mapping: a dictionary (of strings) that maps exchange methods
                        to service methods.
        """
        global ALL_EXCHANGES
        if not ALL_EXCHANGES.get(service_name, None):
            ALL_EXCHANGES[service_name] = []
        self.service_exchanges = ALL_EXCHANGES[service_name]
        self.mapping = mapping

    def __call__(self, exchange):
        """
        :param exchange: the decorated exchange
        :return: the original exchange
        """
        if exchange not in self.service_exchanges:
            self.service_exchanges.append({'exchange': exchange,
                                           'mapping': self.mapping})
        return exchange
